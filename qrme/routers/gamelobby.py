"""The lobby: more than one synthetic thing in a game session.

Authorization here is about **who may put a voice in a match**, and there are
two separate consents rather than one.

The **session owner** decides who is in their lobby — it is their session.
But bringing a *profile* in speaks in that profile's voice, so its **owner**
must consent too, exactly as bringing one into a watch party does. The same
goes for an agent: a running workflow belongs to somebody, and seating it in a
match is a use of it.

Neither check subsumes the other. A session owner who could seat anybody's
profile could put words in a stranger's persona's mouth in front of a lobby of
people; a profile owner who could seat themselves anywhere would be joining
matches uninvited.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import auth, db, gamelobby
from ..common import require_owner, require_self
from .. import i18n

router = APIRouter()


class SeatIn(BaseModel):
    member_kind: str
    member_id: str
    role: str = "teammate"
    callsign: str | None = Field(default=None, max_length=40)


class LeaveIn(BaseModel):
    member_id: str


def _session_or_404(session_id: str) -> dict:
    row = db.connect().execute("SELECT * FROM game_sessions WHERE id=?",
                               (session_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "game session not found")
    return dict(row)


def _same_account(session_profile_id: str, member_profile_id: str) -> None:
    """Both profiles belong to one person, or the seat is refused.

    Checked on `profiles.owner_id`, which is the account. Somebody else's
    profile is a two-party question with a consent on each side, and
    `qrme/sharing.py` is where that already lives — answering half of it here
    would be a second, weaker version of the same negotiation.
    """
    conn = db.connect()
    rows = {r["id"]: r["owner_id"] for r in conn.execute(
        "SELECT id, owner_id FROM profiles WHERE id IN (?,?)",
        (session_profile_id, member_profile_id)).fetchall()}
    if member_profile_id not in rows:
        raise HTTPException(404, "no such profile")
    if rows.get(session_profile_id) != rows[member_profile_id]:
        raise HTTPException(
            403, "that profile is not yours. Bringing somebody else's into "
                 "your session is a two-party agreement — see the skill-grant "
                 "routes, which already ask both sides")


def _in_lobby(session_id: str, request: Request) -> str:
    """The caller must be the session's owner or somebody seated in it."""
    session = _session_or_404(session_id)
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who == {"role": "owner", "subject_id": session["profile_id"]}:
        return who["subject_id"]
    seated = db.connect().execute(
        "SELECT 1 FROM game_lobby WHERE session_id=? AND member_id=?"
        " AND left_at IS NULL", (session_id, who["subject_id"])).fetchone()
    if seated is None:
        raise HTTPException(403, "you are not in this lobby")
    return who["subject_id"]


@router.get("/gaming/lobby/vocabulary")
def vocabulary() -> dict:
    """What can hold a seat, what a seat is for, and what nothing here can do.

    Open — it describes the feature. `never` is the part worth publishing: the
    absence of input, aim assist, macros, automation and exploits is the whole
    difference between a coach and a cheat, and a limit nobody can read is a
    limit nobody can rely on.
    """
    return {
        "kinds": [{"kind": k, "is": v} for k, v in gamelobby.KINDS.items()],
        "seats": [{"role": k, "does": v} for k, v in gamelobby.SEATS.items()],
        "max_synthetic": gamelobby.MAX_SYNTHETIC,
        "never": [{"thing": k, "means": v}
                  for k, v in gamelobby.NEVER.items()],
        "fair_play": gamelobby.FAIR_PLAY,
        "rules": [
            "every member says whether it is a person, a profile or an agent",
            "a profile's own owner consents before it takes a seat",
            f"at most {gamelobby.MAX_SYNTHETIC} synthetic members, counting "
            "the session's own profile",
            "a minor anywhere in the lobby makes the whole lobby strict",
            "members observe and talk — nothing here plays",
        ],
    }


@router.post("/gaming/sessions/{session_id}/lobby", status_code=201)
def seat(session_id: str, body: SeatIn, request: Request) -> dict:
    """Seat a member. Two consents, and neither replaces the other."""
    session = _session_or_404(session_id)
    # It is the session owner's lobby.
    require_owner(session["profile_id"], request)

    # And bringing a profile or an agent in *uses* it, so it has to be one the
    # caller actually holds. A session owner who could seat anybody's profile
    # could put words in a stranger's persona's mouth in front of a lobby of
    # people.
    #
    # "Holds" means **the same account owns both**, checked on `owner_id`
    # rather than on the token. An owner token's subject is a single profile
    # id, so requiring the caller to hold the member's token *and* the
    # session's would mean the two could only ever be the same profile — a
    # check that reads as strict and in fact makes the whole feature
    # impossible. One person's several profiles is exactly the case this is
    # for.
    #
    # Somebody *else's* profile is a two-party question and this is not the
    # module that answers it: `qrme/sharing.py` already lends a skill inside a
    # surface both people are in, with a consent each. Refused here with a
    # pointer rather than half-answered.
    if body.member_kind == "profile":
        if body.member_id != session["profile_id"]:
            _same_account(session["profile_id"], body.member_id)
    elif body.member_kind == "agent":
        row = db.connect().execute(
            "SELECT profile_id FROM workflows WHERE id=?",
            (body.member_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "no such agent")
        if row["profile_id"] != session["profile_id"]:
            _same_account(session["profile_id"], row["profile_id"])
    elif body.member_kind == "player":
        # A real person is seated by themselves, not by somebody else — a seat
        # taken on your behalf is a claim that you are in a match you may not
        # have joined.
        require_self(body.member_id, request)

    try:
        return gamelobby.seat(session_id, body.member_kind, body.member_id,
                              body.role, body.callsign)
    except gamelobby.LobbyError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.get("/gaming/sessions/{session_id}/lobby")
def roster(session_id: str, request: Request) -> dict:
    """Everyone in the lobby and what each one is.

    Readable by the session owner and by anybody seated in it. Who is
    synthetic in a match you are playing is exactly the sort of thing the
    people in that match are owed.
    """
    _in_lobby(session_id, request)
    return gamelobby.roster(session_id)


@router.delete("/gaming/sessions/{session_id}/lobby")
def leave(session_id: str, body: LeaveIn, request: Request) -> dict:
    """Take a member out. The session owner may; a player may remove
    themselves."""
    session = _session_or_404(session_id)
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if (who != {"role": "owner", "subject_id": session["profile_id"]}
            and who["subject_id"] != body.member_id):
        raise HTTPException(403, "not yours to remove")
    return gamelobby.leave(session_id, body.member_id)


@router.get("/gaming/sessions/{session_id}/lobby/context")
def context(session_id: str, request: Request) -> dict:
    """What a synthetic member here is told about its own position.

    It is told that some of the others are synthetic too. A model that
    believes every callsign is a person will address them as people, and a
    lobby that reads as five friends when it is one player and four generated
    voices is the impression this product must not create.
    """
    _in_lobby(session_id, request)
    try:
        return gamelobby.prompt_context(session_id)
    except gamelobby.LobbyError as exc:
        raise HTTPException(404, i18n.raised(exc)) from None
