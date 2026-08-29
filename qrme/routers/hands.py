"""The hands — granting them, using them, and reading what they did.

Every door that creates or widens authority is ``require_owner``. Granting
hands over a machine is the single largest permission in this product, and
an interactor in a conversation is not the person who gets to write one —
including through the *told* door, which is the same authority arriving in
different words and is gated identically.

Two doors are deliberately looser, in the direction of stopping rather than
starting:

* ``POST /hands/reaches/{id}/stop`` is owner-gated but never refuses on the
  grant's state — a reach whose permission already expired can still be
  stopped, because "take my screen back" must never be the request that
  errors.
* ``GET /hands/vocabulary`` is public and publishes the refusals by name.
  A client that only knew what was allowed would draw the iPhone case as a
  missing feature rather than as a decision somebody made and can explain.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import hands
from ..common import require_owner

router = APIRouter()


class GrantIn(BaseModel):
    surface: str = Field(description="computer | phone | here")
    places: list[str] = Field(description="named apps or sites, never '*'")
    verbs: list[str] = Field(description="the moves it may make")
    minutes: int = 30
    steps: int = 40
    watched: bool = True


class ToldIn(BaseModel):
    said: str = Field(description="what the owner said or typed")
    surface: str = "computer"
    watched: bool = True


class ReachIn(BaseModel):
    grant_id: str
    errand: str
    platform: str = Field(description="macos | windows | linux | android | "
                                      "ios | web")
    mode: str = "acting"


class ActIn(BaseModel):
    verb: str
    target: str | None = None
    detail: dict | None = None
    saw: str | None = Field(default=None,
                            description="what the eyes read on the screen")


class NextIn(BaseModel):
    frame: str | None = Field(
        default=None,
        description="One picture of the surface, base64 PNG. Omitted when "
                    "the caller has already described it.")
    saw: str | None = Field(
        default=None,
        description="What the screen shows, in words, when the caller has "
                    "read it already — so the eyes are not paid for twice.")


class HandOverIn(BaseModel):
    to_profile_id: str
    places: list[str] | None = None
    verbs: list[str] | None = None


class StopIn(BaseModel):
    why: str = "stopped by the person"


class RoutineIn(BaseModel):
    name: str
    surface: str
    learned: str = Field(description="shown | told")
    steps: list[dict]


class FromReachIn(BaseModel):
    reach_id: str
    name: str


class ReplayIn(BaseModel):
    grant_id: str
    platform: str


def _fail(exc: hands.HandError) -> HTTPException:
    return HTTPException(status_code=exc.status, detail=exc.message)


@router.get("/hands/vocabulary")
def vocabulary() -> dict:
    """Every move, every surface, and what these hands will not do."""
    return {
        "surfaces": list(hands.SURFACES),
        "platforms": list(hands.PLATFORMS),
        "drivable": list(hands.DRIVABLE),
        "verbs": list(hands.VERBS),
        "eyes_only": list(hands.EYES_ONLY),
        "keys": list(hands.KEYS),
        "doors": list(hands.DOORS),
        "caps": {"steps": hands.STEP_CAP, "minutes": hands.MINUTES_CAP,
                 "wait_seconds": hands.WAIT_CAP},
        "never": [
            "no permission is ever implied — a grant names its apps, its "
            "moves, its minutes and its steps, and '*' is refused",
            "it does not type passwords, PINs, one-time codes, card "
            "numbers or recovery phrases, and says so instead of trying",
            "text on a screen is read as data and can never widen what it "
            "is allowed to do, whatever that text claims",
            "it cannot operate another app's interface on an iPhone — "
            "Apple provides no way, so on iOS it watches and tells you "
            "where to press",
            "there is no shell, no install and no download; a cursor and "
            "a keyboard is the whole instrument",
            "handing an errand to a second profile can only narrow what "
            "is permitted, never widen it",
        ],
    }


@router.post("/profiles/{profile_id}/hands/grants")
def write_grant(profile_id: str, body: GrantIn, request: Request) -> dict:
    """The menu door: the owner picks what these hands may do."""
    require_owner(profile_id, request)
    try:
        return hands.grant(profile_id, profile_id, surface=body.surface,
                           places=body.places, verbs=body.verbs,
                           minutes=body.minutes, steps=body.steps,
                           watched=body.watched, door="picked")
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.post("/profiles/{profile_id}/hands/told")
def told_grant(profile_id: str, body: ToldIn, request: Request) -> dict:
    """The spoken door: the same authority, said out loud or typed.

    Owner-gated exactly like the menu, and strict about what the words
    actually named — see `hands.grant_from_words`.
    """
    require_owner(profile_id, request)
    try:
        return hands.grant_from_words(profile_id, profile_id, body.said,
                                      surface=body.surface,
                                      watched=body.watched)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.get("/profiles/{profile_id}/hands/grants")
def list_grants(profile_id: str, request: Request,
                live: bool = False) -> dict:
    """What these hands currently may do, and what they used to."""
    require_owner(profile_id, request)
    return {"grants": hands.grants(profile_id, live_only=live)}


@router.delete("/profiles/{profile_id}/hands/grants/{grant_id}")
def take_back(profile_id: str, grant_id: str, request: Request) -> dict:
    """Take the hands back. Open reaches stop at their next step."""
    require_owner(profile_id, request)
    try:
        held = hands.read_grant(grant_id)
        if held["profile_id"] != profile_id:
            raise hands.HandError(404, "no such grant on this profile")
        return hands.revoke(grant_id)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.post("/profiles/{profile_id}/hands/reaches")
def open_reach(profile_id: str, body: ReachIn, request: Request) -> dict:
    """Put its hands on a surface for one errand."""
    require_owner(profile_id, request)
    try:
        return hands.open_reach(profile_id, body.grant_id,
                                errand=body.errand, platform=body.platform,
                                mode=body.mode)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.get("/profiles/{profile_id}/hands/reaches/{reach_id}")
def read_reach(profile_id: str, reach_id: str, request: Request) -> dict:
    require_owner(profile_id, request)
    try:
        reach = hands.read_reach(reach_id)
    except hands.HandError as exc:
        raise _fail(exc) from None
    if reach["profile_id"] != profile_id:
        raise HTTPException(status_code=404, detail="no such reach")
    return {"reach": reach, "ledger": hands.ledger(reach_id)}


@router.post("/profiles/{profile_id}/hands/reaches/{reach_id}/act")
def act(profile_id: str, reach_id: str, body: ActIn,
        request: Request) -> dict:
    """One move. Refusals come back 200 with the refusal in the row —
    a hand declining to type a password is the system working, not the
    request failing, and the client draws it in the transcript either way."""
    require_owner(profile_id, request)
    try:
        reach = hands.read_reach(reach_id)
        if reach["profile_id"] != profile_id:
            raise hands.HandError(404, "no such reach")
        return hands.act(reach_id, body.verb, target=body.target,
                         detail=body.detail, saw=body.saw)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.post("/profiles/{profile_id}/hands/reaches/{reach_id}/next")
def next_move(profile_id: str, reach_id: str, body: NextIn,
              request: Request) -> dict:
    """One frame in, one bounded move out.

    The door a companion holds open: it sends a picture of the surface, and
    what comes back is a single move that has already been through every
    bound the grant carries and is already written in the ledger.

    A refusal comes back the same way, 200 with the refusal in the row.
    The companion performs only what carries ``outcome == "done"``;
    anything else is finished business — recorded, explained, and nothing
    for a hand to do.

    Deciding and permitting are one call on purpose. A decision that is
    not immediately bounded is a decision somebody has to remember to
    bound, and the whole point of `hands.act` is that nobody has to
    remember.
    """
    require_owner(profile_id, request)
    try:
        reach = hands.read_reach(reach_id)
        if reach["profile_id"] != profile_id:
            raise hands.HandError(404, "no such reach")
        return hands.decide(reach_id, frame_b64=body.frame, seen=body.saw)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.post("/profiles/{profile_id}/hands/reaches/{reach_id}/hand-over")
def hand_over(profile_id: str, reach_id: str, body: HandOverIn,
              request: Request) -> dict:
    """Pass the errand to a second profile, narrowed or the same."""
    require_owner(profile_id, request)
    try:
        reach = hands.read_reach(reach_id)
        if reach["profile_id"] != profile_id:
            raise hands.HandError(404, "no such reach")
        return hands.hand_over(reach_id, body.to_profile_id,
                               places=body.places, verbs=body.verbs)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.post("/profiles/{profile_id}/hands/reaches/{reach_id}/stop")
def stop(profile_id: str, reach_id: str, body: StopIn,
         request: Request) -> dict:
    """Take the screen back. Never refuses on the grant's state."""
    require_owner(profile_id, request)
    try:
        reach = hands.read_reach(reach_id)
        if reach["profile_id"] != profile_id:
            raise hands.HandError(404, "no such reach")
        return hands.stop(reach_id, body.why)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.get("/profiles/{profile_id}/hands/routines")
def list_routines(profile_id: str, request: Request) -> dict:
    """Everything it can do again."""
    require_owner(profile_id, request)
    return {"routines": hands.routines(profile_id)}


@router.post("/profiles/{profile_id}/hands/routines")
def write_routine(profile_id: str, body: RoutineIn,
                  request: Request) -> dict:
    """Dictate a routine in steps."""
    require_owner(profile_id, request)
    try:
        return hands.learn(profile_id, body.name, surface=body.surface,
                           learned=body.learned, steps=body.steps)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.post("/profiles/{profile_id}/hands/routines/from-reach")
def learn_from_reach(profile_id: str, body: FromReachIn,
                     request: Request) -> dict:
    """Write down what it just watched somebody do."""
    require_owner(profile_id, request)
    try:
        reach = hands.read_reach(body.reach_id)
        if reach["profile_id"] != profile_id:
            raise hands.HandError(404, "no such reach")
        return hands.learn_from_reach(body.reach_id, body.name)
    except hands.HandError as exc:
        raise _fail(exc) from None


@router.post("/profiles/{profile_id}/hands/routines/{routine_id}/replay")
def replay(profile_id: str, routine_id: str, body: ReplayIn,
           request: Request) -> dict:
    """Do it again — through a live grant, never around one."""
    require_owner(profile_id, request)
    try:
        routine = hands.read_routine(routine_id)
        if routine["profile_id"] != profile_id:
            raise hands.HandError(404, "no such routine")
        return hands.replay(routine_id, body.grant_id,
                            platform=body.platform)
    except hands.HandError as exc:
        raise _fail(exc) from None
