"""More than one synthetic thing in a game session.

The single-companion version is a conversation. A roster is a different thing,
and the tests that matter are the ones about what changes when you add a
second one: fair play stops being a prompt line and becomes a countable
property, and the honesty rule stops being about one profile and becomes about
a lobby where you cannot tell the callsigns apart.
"""

import pytest

from qrme import db, gamelobby
from tests.test_capabilities import auth_header, make_profile


def _interactor(client, name="Sam", birthdate="1990-01-01"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": birthdate})
    assert r.status_code == 201, r.text
    return r.json()


def _as(token):
    return {"authorization": f"Bearer {token}"}


def _session(client, profile):
    r = client.post(f"/profiles/{profile['id']}/gaming/sessions",
                    json={"platform": "steam", "game": "Sundered Reach",
                          "role": "teammate"}, headers=auth_header(profile))
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _workflow(profile_id, status="running"):
    conn = db.connect()
    wid = db.new_id("wfl")
    conn.execute(
        "INSERT INTO workflows (id, profile_id, goal, plan, status,"
        " created_at, updated_at) VALUES (?,?,?,'[]',?,?,?)",
        (wid, profile_id, "watch my positioning", status, db.utcnow(),
         db.utcnow()))
    conn.commit()
    return wid


# -- the roster ---------------------------------------------------------------

def test_a_session_can_hold_several_of_your_own_profiles_and_agents(client):
    """The whole point of this module. `game_sessions` seats exactly one
    profile; this is the roster beside the real players.

    Your own, and "own" means the same account — checked on `owner_id`, not on
    the token. An owner token's subject is a single profile id, so requiring
    the caller to hold both the session's token and the member's would mean
    the two could only ever be the same profile: a check that reads as strict
    and in fact makes the feature impossible. One person's several profiles is
    exactly the case this is for.
    """
    host = make_profile(client, owner_id="o1", display_name="Vex")
    mine = make_profile(client, owner_id="o1", display_name="Rook")
    sid = _session(client, host)

    r = client.post(f"/gaming/sessions/{sid}/lobby",
                    json={"member_kind": "profile", "member_id": mine["id"],
                          "role": "coach"}, headers=auth_header(host))
    assert r.status_code == 201, r.text

    client.post(f"/gaming/sessions/{sid}/lobby",
                json={"member_kind": "agent",
                      "member_id": _workflow(host["id"]), "role": "spotter"},
                headers=auth_header(host))

    board = client.get(f"/gaming/sessions/{sid}/lobby",
                       headers=auth_header(host)).json()
    assert board["profiles"] == 2 and board["agents"] == 1
    assert board["members"][0]["host"] is True


def test_the_session_profile_is_derived_not_stored(client):
    """A copy of it in `game_lobby` would be a second place the same fact
    lives, and the day the two disagree the roster would show a session hosted
    by a profile the session does not think it has."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    board = gamelobby.roster(sid)

    assert board["members"][0]["member_id"] == host["id"]
    assert board["members"][0]["seat_id"] is None       # derived
    rows = db.connect().execute(
        "SELECT COUNT(*) AS n FROM game_lobby WHERE session_id=?",
        (sid,)).fetchone()["n"]
    assert rows == 0


def test_every_member_says_what_it_is(client):
    """A lobby where you cannot tell which of the callsigns is a person is the
    one this platform exists not to build — and it is worse here than in a
    chat room, because the others in a match did not opt into anything."""
    host = make_profile(client, display_name="Vex")
    sam = _interactor(client)
    sid = _session(client, host)
    wid = _workflow(host["id"])

    client.post(f"/gaming/sessions/{sid}/lobby",
                json={"member_kind": "agent", "member_id": wid,
                      "role": "spotter"}, headers=auth_header(host))
    gamelobby.seat(sid, "player", sam["id"], "teammate", callsign="samhain")

    kinds = {m["member_id"]: m["synthetic"]
             for m in gamelobby.roster(sid)["members"]}
    assert kinds[host["id"]] is True     # the session's own profile
    assert kinds[wid] is True            # the agent
    assert kinds[sam["id"]] is False     # the person


def test_an_agent_carries_its_light(client):
    """A member that has stopped and is waiting on somebody must not look, on
    the roster, exactly like one that is working."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    waiting = _workflow(host["id"], status="awaiting_input")
    gamelobby.seat(sid, "agent", waiting, "coach")

    agent = [m for m in gamelobby.roster(sid)["members"]
             if m["member_kind"] == "agent"][0]
    assert agent["light"]["light"] == "amber"
    assert agent["light"]["needs_you"] is True


# -- fair play, which is what changes when you add a second one ---------------

def test_synthetic_members_are_capped(client):
    """Not for load. A lobby where the synthetic side outnumbers the humans
    has stopped being people playing with help and become an operation being
    run, whatever any single line says."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    # The session's own profile counts as one, so MAX_SYNTHETIC - 1 more fit.
    for _ in range(gamelobby.MAX_SYNTHETIC - 1):
        gamelobby.seat(sid, "agent", _workflow(host["id"]), "spotter")

    with pytest.raises(gamelobby.LobbyError) as exc:
        gamelobby.seat(sid, "agent", _workflow(host["id"]), "spotter")
    assert "operation being run" in str(exc.value)


def test_the_cap_counts_the_sessions_own_profile(client):
    """Counting only the table would let the cap be one higher than the number
    the roster actually shows — the sort of off-by-one that turns a stated
    limit into a lie about itself."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    for _ in range(gamelobby.MAX_SYNTHETIC - 1):
        gamelobby.seat(sid, "agent", _workflow(host["id"]), "spotter")

    board = gamelobby.roster(sid)
    synthetic = [m for m in board["members"] if m["synthetic"]]
    assert len(synthetic) == gamelobby.MAX_SYNTHETIC
    assert board["synthetic_seats_left"] == 0


def test_a_player_never_counts_against_the_cap(client):
    """The limit is on the synthetic side. A squad of real people is a squad."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    for i in range(6):
        who = _interactor(client, f"P{i}")
        gamelobby.seat(sid, "player", who["id"], "teammate")
    assert gamelobby.roster(sid)["people"] == 6
    assert gamelobby.roster(sid)["synthetic_seats_left"] == 3


def test_nothing_here_can_act_in_a_game(client):
    """The line between a coach and a cheat, asserted by name.

    "We did not add that" is a fact about today; this is what makes it a fact
    about tomorrow. Every one of these words appearing as a *capability* in
    this module would be automation in the plainest sense.
    """
    import inspect

    from qrme import gamelobby as mod
    from qrme.routers import gamelobby as router_mod

    for module in (mod, router_mod):
        src = inspect.getsource(module)
        # Not a substring sweep — the words appear in the prose that forbids
        # them. Functions are the surface that could actually do it.
        names = [n for n, obj in vars(module).items()
                 if inspect.isfunction(obj)]
        for banned in ("press", "send_input", "aim", "macro", "act",
                       "fire", "move", "click"):
            assert not any(banned in n for n in names), (
                f"{module.__name__} grew a function named for {banned!r}")

    assert set(gamelobby.NEVER) == {"input", "aim", "macro", "automation",
                                    "exploit"}
    assert "Nothing in it plays" in gamelobby.FAIR_PLAY


def test_the_prompt_tells_a_member_the_others_may_be_synthetic(client):
    """A model that believes every callsign is a person will address them as
    people, and a lobby that reads as five friends when it is one player and
    four generated voices is the impression this product must not create."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    gamelobby.seat(sid, "agent", _workflow(host["id"]), "coach")

    ctx = gamelobby.prompt_context(sid)
    assert "some of the others are synthetic too" in ctx["instruction"]
    assert "cannot press a button" in ctx["instruction"]
    assert ctx["synthetic_here"] >= 1


def test_a_minor_anywhere_in_the_lobby_makes_it_strict(client):
    """Team comms faces whoever is in the match, and it keys on the lobby
    rather than the session's owner — the person a line might land badly on is
    the one sitting in it, not the one who started it."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    assert gamelobby.maturity(sid) == "balanced"

    kid = _interactor(client, "Junior", birthdate="2014-01-01")
    gamelobby.seat(sid, "player", kid["id"], "teammate")
    assert gamelobby.maturity(sid) == "strict"
    assert gamelobby.roster(sid)["maturity"] == "strict"


# -- who may seat whom --------------------------------------------------------

def test_a_session_owner_cannot_seat_somebody_elses_profile(client):
    """It would put words in a stranger's persona's mouth in front of a lobby
    of people. Refused with a pointer at the two-party flow that already
    exists, rather than half-answered here."""
    host = make_profile(client, owner_id="o1", display_name="Vex")
    stranger = make_profile(client, owner_id="o2", display_name="Rook")
    sid = _session(client, host)

    r = client.post(f"/gaming/sessions/{sid}/lobby",
                    json={"member_kind": "profile",
                          "member_id": stranger["id"], "role": "coach"},
                    headers=auth_header(host))
    assert r.status_code == 403
    assert "two-party" in r.json()["detail"]


def test_an_agent_belonging_to_somebody_else_is_refused_too(client):
    """A running workflow belongs to somebody, and seating it in a match is a
    use of it."""
    host = make_profile(client, owner_id="o1", display_name="Vex")
    stranger = make_profile(client, owner_id="o2", display_name="Rook")
    sid = _session(client, host)
    theirs = _workflow(stranger["id"])

    r = client.post(f"/gaming/sessions/{sid}/lobby",
                    json={"member_kind": "agent", "member_id": theirs,
                          "role": "coach"}, headers=auth_header(host))
    assert r.status_code == 403


def test_a_profile_owner_cannot_seat_themselves_in_a_stranger_session(client):
    """The other direction: joining matches uninvited."""
    host = make_profile(client, owner_id="o1", display_name="Vex")
    stranger = make_profile(client, owner_id="o2", display_name="Rook")
    sid = _session(client, host)

    r = client.post(f"/gaming/sessions/{sid}/lobby",
                    json={"member_kind": "profile",
                          "member_id": stranger["id"], "role": "coach"},
                    headers=auth_header(stranger))
    assert r.status_code == 403


def test_a_seat_cannot_be_taken_on_a_persons_behalf(client):
    """A seat taken for you is a claim that you are in a match you may not
    have joined."""
    host = make_profile(client, display_name="Vex")
    sam = _interactor(client)
    sid = _session(client, host)
    r = client.post(f"/gaming/sessions/{sid}/lobby",
                    json={"member_kind": "player", "member_id": sam["id"]},
                    headers=auth_header(host))
    assert r.status_code == 403


def test_the_roster_is_for_the_people_in_the_match(client):
    """Who is synthetic in a match you are playing is exactly what the people
    in that match are owed — and nobody else's business."""
    host = make_profile(client, display_name="Vex")
    sam = _interactor(client)
    outsider = _interactor(client, "Nosy")
    sid = _session(client, host)
    gamelobby.seat(sid, "player", sam["id"], "teammate")

    assert client.get(f"/gaming/sessions/{sid}/lobby",
                      headers={"authorization": ""}).status_code == 401
    assert client.get(f"/gaming/sessions/{sid}/lobby",
                      headers=_as(outsider["token"])).status_code == 403
    assert client.get(f"/gaming/sessions/{sid}/lobby",
                      headers=_as(sam["token"])).status_code == 200


def test_a_player_can_remove_themselves(client):
    host = make_profile(client, display_name="Vex")
    sam = _interactor(client)
    sid = _session(client, host)
    gamelobby.seat(sid, "player", sam["id"], "teammate")

    out = client.request("DELETE", f"/gaming/sessions/{sid}/lobby",
                         json={"member_id": sam["id"]},
                         headers=_as(sam["token"]))
    assert out.status_code == 200 and out.json()["seated"] is False


# -- ending -------------------------------------------------------------------

def test_the_lobby_empties_when_the_session_ends(client):
    """A seat that survived the match would put a synthetic member in the next
    one without anybody asking for it."""
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    gamelobby.seat(sid, "agent", _workflow(host["id"]), "coach")

    out = client.post(f"/gaming/sessions/{sid}/end",
                      headers=auth_header(host)).json()
    assert out["lobby_emptied"] == 1
    assert gamelobby.roster(sid)["agents"] == 0


def test_an_ended_session_takes_no_new_member(client):
    host = make_profile(client, display_name="Vex")
    sid = _session(client, host)
    client.post(f"/gaming/sessions/{sid}/end", headers=auth_header(host))
    with pytest.raises(gamelobby.LobbyError):
        gamelobby.seat(sid, "agent", _workflow(host["id"]), "coach")


def test_the_vocabulary_publishes_what_nothing_here_can_do(client):
    """A limit nobody can read is a limit nobody can rely on."""
    out = client.get("/gaming/lobby/vocabulary").json()
    never = {n["thing"] for n in out["never"]}
    assert never == {"input", "aim", "macro", "automation", "exploit"}
    assert out["max_synthetic"] == gamelobby.MAX_SYNTHETIC
