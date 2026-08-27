"""More than one synthetic thing in a game session.

`qrme/routers/gaming.py` puts **one** profile alongside a player: a companion,
a teammate, a practice partner. That is a conversation. This is the roster —
several synthetic profiles *and* running agents in the same session, with the
real players, which is a different thing and raises a question the single-seat
version never had to answer.

**The question is fair play, and it changes shape when you add a second one.**
A companion calling shots is a teammate talking. Five of them coordinating on
one player's behalf is indistinguishable, from the game publisher's side, from
a bot squad — and this platform's fair-play rule is already *absolute* rather
than a toggle. So the roster carries two hard limits that a single companion
never needed:

**Synthetic members are capped** (:data:`MAX_SYNTHETIC`). Not for load. A lobby
where the synthetic side outnumbers the humans has stopped being people playing
with help and become an operation being run, whatever each individual line
says.

**Nothing here can act in a game.** Members observe and they talk. There is no
input, no action, no macro, no path from this module to a controller — and a
test asserts the absence by name, because "we did not add that" is a fact about
today and the test is what makes it a fact about tomorrow. An agent that could
*press buttons* would be automation in the plainest sense, and the difference
between a coach and a cheat is exactly that line.

**Every member says what it is.** A player, a synthetic profile, or an agent —
carried on every read, never inferred from a name. A lobby where you cannot
tell which of the callsigns is a person is the lobby this platform exists not
to build, and it is worse here than in a chat room because the others in a
match did not opt into anything.

**Agents bring their light.** An agent in a lobby is a running workflow, so it
carries the same green/amber/red the rest of the product uses. A member that
has stopped and is waiting on a person should not look, on the roster, exactly
like one that is working.

**A minor anywhere in the lobby makes the whole lobby strict.** Team comms is
a public surface facing whoever is in the match, which is the existing room
rule reaching the surface it matters most on.
"""

from __future__ import annotations

from . import db, i18n

# What can hold a seat.
#
# `agent` is the new one and the reason this module is not just "more
# profiles": a profile is a persona that talks, an agent is a running workflow
# with a goal and a status. They are listed separately because they fail
# differently — a persona says something wrong, an agent stops and waits.
KINDS: dict[str, str] = {
    "player": "a real person",
    "profile": "a synthetic profile — a persona, playing a part",
    "agent": "a running workflow — a goal, a status, and a light",
}
SYNTHETIC_KINDS = ("profile", "agent")

# What a seat is for. Deliberately the roles that describe *talking and
# watching*, because those are the only things anything here can do.
SEATS: dict[str, str] = {
    "companion": "keeps the vibe up and reacts to the moment",
    "teammate": "coordinates and calls the play",
    "practice_partner": "gives honest feedback afterwards",
    "coach": "watches and tells you what it saw",
    "spotter": "watches one thing you asked it to watch",
    "archivist": "keeps the record of what happened",
}

# The cap, and it is about legitimacy rather than load. Four synthetic members
# beside a squad reads as help; a lobby where they outnumber the people has
# become an operation being run, whatever any single line says.
MAX_SYNTHETIC = 4

# The absence that matters, kept as data so a test can assert it by name.
# Nothing in this module produces any of these, and nothing should.
NEVER: dict[str, str] = {
    "input": "no key, button, stick or click is ever sent to a game",
    "aim": "nothing computes or corrects where a player is pointing",
    "macro": "no recorded or generated sequence is played back",
    "automation": "no member takes a turn, a shot or an action",
    "exploit": "nothing here knows or offers a bug, glitch or cheat",
    # The two that close the hardware answer to the rule above. Everything
    # before this line is about what a member *does*; these are about what a
    # member *is allowed to be* in a match, and they exist because the obvious
    # way round "no automation" is to stop calling it automation.
    "player_slot": "no synthetic member occupies a player slot in a two-, "
                   "three- or any-player game — they are beside the players, "
                   "never among them",
    "own_hardware": "and not from a console, PC, handheld or instance of its "
                    "own either. A second machine does not turn a bot into a "
                    "player; it just moves where the bot is running",
    # The rest of the plumbing, named individually. Every one of these is the
    # same act — a synthetic thing driving a character — and each arrives
    # wearing a different word, so refusing the act generically is not enough.
    # Somebody proposing one of these will say "it is only a controller", "it
    # is only a capture card", "it is only a plug-in", and the refusal has to
    # meet them in that vocabulary.
    "second_controller": "a second pad, stick or wheel on the same console is "
                         "the same bot with a shorter cable — one player, one "
                         "controller, and a controller nobody is holding is "
                         "not a player's",
    "bluetooth_input": "pairing a synthetic member to a console as an input "
                       "device is the second controller again, wireless. The "
                       "pairing is the tell, not the cable",
    "capture_perception": "a capture card or video-in feeding the game's "
                          "picture to a member is how it would learn where to "
                          "aim. Watching the screen to play is playing",
    "game_plugin": "an overlay, mod, injector or plug-in that hands a member "
                   "the game's state or its controls, whatever it is called "
                   "and whoever wrote it",
    "own_character": "no member pilots a character. Not a second character "
                     "beside the player's, not a co-op partner, not a body "
                     "in the world — the player's character is the only one "
                     "this platform's account is behind",
}

FAIR_PLAY = (
    "Everything in this lobby observes and talks. Nothing in it plays. No "
    "member sends an input to the game, corrects anybody's aim, or takes an "
    "action on a player's behalf — that is the line between a coach and a "
    "cheat, and it is a property of the code rather than a setting. No "
    "synthetic member occupies a player slot in a multiplayer game, and no "
    "amount of hardware changes that: not a console of its own, not a second "
    "controller on yours, not a Bluetooth pad paired to it, not a capture "
    "card feeding it the picture, not a plug-in handing it the controls. "
    "Every one of those is the same bot with different plumbing, and none of "
    "them pilots a character beside you."
)

# The seats a synthetic member may hold. A `player` seat is a person's, and
# nothing else may take one — which is the rule above expressed as data rather
# than left to a prompt to honour.
SYNTHETIC_SEATS = ("companion", "practice_partner", "coach", "spotter",
                   "archivist")


class LobbyError(ValueError):
    """A seat that must not be filled. Text meant for a person."""


def _session(session_id: str) -> dict:
    row = db.connect().execute("SELECT * FROM game_sessions WHERE id=?",
                               (session_id,)).fetchone()
    if row is None:
        raise LobbyError("no such game session")
    return dict(row)


def seat(session_id: str, member_kind: str, member_id: str,
         role: str = "teammate", callsign: str | None = None) -> dict:
    """Take a seat in this session's lobby.

    The session's own profile is *not* seated here — :func:`roster` derives it
    from the session row instead, so a lobby can never show a session missing
    the companion it was started with, and the two can never disagree about
    which profile that is.
    """
    session = _session(session_id)
    if session["status"] != "active":
        raise LobbyError("that session has ended")
    if member_kind not in KINDS:
        raise LobbyError(
            i18n.fill(i18n.UNKNOWN_CHOICE_DASH, field="member kind", got=repr(member_kind), choices=', '.join(KINDS)))
    if role not in SEATS:
        raise LobbyError(i18n.fill(i18n.UNKNOWN_CHOICE_DASH, field="seat", got=repr(role), choices=', '.join(SEATS)))

    # A `teammate` seat is a player's seat: it is the one that means *in the
    # match, on the roster, taking a slot*. Nothing synthetic may hold one, and
    # that is checked here rather than trusted to a prompt, because the whole
    # point of the rule is that it survives a model deciding otherwise.
    if member_kind in SYNTHETIC_KINDS and role not in SYNTHETIC_SEATS:
        raise LobbyError(
            i18n.fill(i18n.GAME_SEAT, kind=KINDS[member_kind].split(' —')[0], seat=repr(role), role=', '.join(SYNTHETIC_SEATS)))

    conn = db.connect()
    if member_kind == "profile":
        if conn.execute("SELECT 1 FROM profiles WHERE id=?",
                        (member_id,)).fetchone() is None:
            raise LobbyError("no such profile")
    if member_kind == "agent":
        if conn.execute("SELECT 1 FROM workflows WHERE id=?",
                        (member_id,)).fetchone() is None:
            raise LobbyError("no such agent")

    already = conn.execute(
        "SELECT id FROM game_lobby WHERE session_id=? AND member_id=?"
        " AND left_at IS NULL", (session_id, member_id)).fetchone()
    if already:
        return {**_read(conn.execute("SELECT * FROM game_lobby WHERE id=?",
                                     (already["id"],)).fetchone()),
                "already_seated": True}

    if member_kind in SYNTHETIC_KINDS:
        # +1 for the session's own profile, which `roster` derives rather than
        # storing. Counting only the table would let the cap be one higher than
        # the number the roster actually shows, which is the sort of off-by-one
        # that turns a stated limit into a lie about itself.
        live = 1 + conn.execute(
            "SELECT COUNT(*) AS n FROM game_lobby WHERE session_id=?"
            " AND left_at IS NULL AND member_kind IN ('profile','agent')",
            (session_id,)).fetchone()["n"]
        if live >= MAX_SYNTHETIC:
            raise LobbyError(
                i18n.fill(i18n.SYNTH_MEMBERS_LIMIT, max=MAX_SYNTHETIC))

    seat_id = db.new_id("gsl")
    conn.execute(
        "INSERT INTO game_lobby (id, session_id, member_kind, member_id,"
        " role, callsign, joined_at) VALUES (?,?,?,?,?,?,?)",
        (seat_id, session_id, member_kind, member_id, role, callsign,
         db.utcnow()))
    conn.commit()
    return {**worn(seat_id), "seated": True}


def leave(session_id: str, member_id: str) -> dict:
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM game_lobby WHERE session_id=? AND member_id=?"
        " AND left_at IS NULL", (session_id, member_id)).fetchone()
    if row is None:
        return {"seated": False, "note": "that member was not in the lobby"}
    conn.execute("UPDATE game_lobby SET left_at=? WHERE id=?",
                 (db.utcnow(), row["id"]))
    conn.commit()
    return {"seated": False, "id": row["id"]}


def close(session_id: str) -> int:
    """Empty the lobby when the session ends."""
    conn = db.connect()
    n = conn.execute(
        "SELECT COUNT(*) AS n FROM game_lobby WHERE session_id=?"
        " AND left_at IS NULL", (session_id,)).fetchone()["n"]
    conn.execute("UPDATE game_lobby SET left_at=? WHERE session_id=?"
                 " AND left_at IS NULL", (db.utcnow(), session_id))
    conn.commit()
    return n


def worn(seat_id: str) -> dict:
    row = db.connect().execute("SELECT * FROM game_lobby WHERE id=?",
                               (seat_id,)).fetchone()
    return _read(row) if row else {}


def _read(row) -> dict:
    from . import agentlight

    kind = row["member_kind"]
    out = {
        "seat_id": row["id"],
        "member_kind": kind,
        "member_id": row["member_id"],
        "role": row["role"],
        "does": SEATS[row["role"]],
        "callsign": row["callsign"],
        # Never inferred from a name and never omitted. A lobby where you
        # cannot tell which of the callsigns is a person is the one this
        # platform exists not to build — and the others in a match did not opt
        # into anything.
        "synthetic": kind in SYNTHETIC_KINDS,
        "is": KINDS[kind],
        "since": row["joined_at"],
    }
    if kind == "agent":
        # An agent is a running workflow, so it carries the same light as
        # everywhere else in the product. A member that has stopped and is
        # waiting on somebody must not look, on the roster, exactly like one
        # that is working.
        wf = db.connect().execute(
            "SELECT status FROM workflows WHERE id=?",
            (row["member_id"],)).fetchone()
        if wf is not None:
            out["light"] = agentlight.light(wf["status"])
    return out


def roster(session_id: str) -> dict:
    """Everyone in the lobby, and what each one is."""
    session = _session(session_id)
    rows = db.connect().execute(
        "SELECT * FROM game_lobby WHERE session_id=? AND left_at IS NULL"
        " ORDER BY joined_at, rowid", (session_id,)).fetchall()

    # The session's own profile, first and derived rather than stored. A copy
    # of it in `game_lobby` would be a second place the same fact lives, and
    # the day the two disagree the roster would show a session hosted by a
    # profile the session does not think it has.
    members = [{
        "seat_id": None,
        "member_kind": "profile",
        "member_id": session["profile_id"],
        "role": session["role"] if session["role"] in SEATS else "companion",
        "does": SEATS.get(session["role"], SEATS["companion"]),
        "callsign": None,
        "synthetic": True,
        "is": KINDS["profile"],
        "host": True,
        "since": session["created_at"],
    }]
    members += [_read(r) for r in rows]
    synthetic = [m for m in members if m["synthetic"]]
    people = [m for m in members if not m["synthetic"]]
    return {
        "session_id": session_id,
        "game": session["game"],
        "platform": session["platform"],
        "seats": members,
        "people": len(people),
        "profiles": len([m for m in members if m["member_kind"] == "profile"]),
        "agents": len([m for m in members if m["member_kind"] == "agent"]),
        "synthetic_seats_left": MAX_SYNTHETIC - len(synthetic),
        "maturity": maturity(session_id),
        "fair_play": FAIR_PLAY,
        "never": [{"thing": k, "means": v} for k, v in NEVER.items()],
    }


def maturity(session_id: str) -> str:
    """Strict if anybody in the lobby is a minor.

    Team comms faces whoever is in the match, so this is the existing room
    rule reaching the surface it matters most on — and it keys on the *lobby*
    rather than on the session's owner, because the person a line might land
    badly on is the one sitting in it, not the one who started it.
    """
    from datetime import date

    from .common import age_of

    rows = db.connect().execute(
        "SELECT member_id FROM game_lobby WHERE session_id=?"
        " AND member_kind='player' AND left_at IS NULL",
        (session_id,)).fetchall()
    conn = db.connect()
    for r in rows:
        who = conn.execute("SELECT birthdate FROM interactors WHERE id=?",
                           (r["member_id"],)).fetchone()
        if who is None or not who["birthdate"]:
            return "strict"
        if age_of(date.fromisoformat(who["birthdate"])) < 18:
            return "strict"
    return "balanced"


def prompt_context(session_id: str) -> dict:
    """What a synthetic member in this lobby is told about its own position.

    It is in a match with other members, some of which are also synthetic, and
    it is told so — the same honesty rule the watch party follows. A model that
    believes every other callsign is a person will address them as people, and
    a lobby that reads as five friends when it is one player and four
    generated voices is the impression this product must not create.
    """
    board = roster(session_id)
    return {
        "game": board["game"],
        "seats": [{"callsign": m["callsign"], "role": m["role"],
                     "synthetic": m["synthetic"]} for m in board["seats"]],
        "people": board["people"],
        "synthetic_here": board["profiles"] + board["agents"],
        "maturity": board["maturity"],
        "instruction": (
            "You are one of several members in this lobby and some of the "
            "others are synthetic too — do not address them as people or "
            "speak as though this were a group of friends. You observe and "
            "you talk; you cannot press a button, take a shot, or act in the "
            "game, so never claim to have done so or offer to. " + FAIR_PLAY),
    }
