"""The desk could be reached and could not do the work.

## The finding

Everything on a desk let a person *reach* it — the card, the bell, the
stream, the printed code on the shop door. Nothing let the desk do the job
those doors exist for. A repair counter's whole trade is "hand me the
thing": the staffer takes the caller's screen, their machine, a program,
and works on it — Geek Squad, for whatever trade the desk is in. QRME had
the counter and no way to pass anything across it.

    asked     can a person reach the desk
    mattered  can the desk then do the work

## The physics kept

The feature is an access grant between strangers, so the shape is the same
one `delegation.py` and `grants.py` already use, held by who authenticates
what rather than by checks someone remembers to write:

* only the **desk's token** opens a session or *offers* a connection — the
  party with the expertise names what it needs;
* only the **caller's token** accepts — it is their machine the link opens
  — and the accept is what mints the link token, returned to them alone;
* either side ends a link or closes the session, and ending **NULLs the
  token in the row**: an ended connection has no secret left to present,
  structurally.
"""

from __future__ import annotations


def _desk(client, **over):
    body = {"owner_id": "own-1", "display_name": "Marcus' Counter",
            "trade": "computer repair", "attestor": "Marcus Bell",
            "basis": "shop licence on file", **over}
    if body.get("rated"):
        # A rated desk can only be opened by the person on it.
        body["attestor"] = body["owner_id"]
    r = client.post("/desks", json=body)
    assert r.status_code == 201, r.text
    made = r.json()
    made["id"] = made["desk_id"]
    return made


def _caller(client, birthdate="1984-06-01"):
    r = client.post("/interactors", json={"display_name": "Vera",
                                          "birthdate": birthdate})
    assert r.status_code == 201, r.text
    return r.json()


def _bearer(token):
    return {"authorization": f"Bearer {token}"}


def _counter(client, rated=False, birthdate="1984-06-01"):
    """A desk, a caller, and an open session between them."""
    desk = _desk(client, rated=rated)
    caller = _caller(client, birthdate=birthdate)
    dh = _bearer(desk["desk_token"])
    ch = _bearer(caller["token"])
    r = client.post(f"/desks/{desk['id']}/sessions",
                    json={"caller_id": caller["id"]}, headers=dh)
    assert r.status_code == 201, r.text
    return desk, caller, dh, ch, r.json()


# --- the counter opens ------------------------------------------------------

def test_only_the_desk_token_opens_a_session(client):
    desk = _desk(client)
    caller = _caller(client)
    r = client.post(f"/desks/{desk['id']}/sessions",
                    json={"caller_id": caller["id"]})
    assert r.status_code == 401, r.text
    r = client.post(f"/desks/{desk['id']}/sessions",
                    json={"caller_id": caller["id"]},
                    headers=_bearer(caller["token"]))
    assert r.status_code == 403, r.text


def test_a_session_needs_a_real_caller(client):
    desk = _desk(client)
    r = client.post(f"/desks/{desk['id']}/sessions",
                    json={"caller_id": "made-up"},
                    headers=_bearer(desk["desk_token"]))
    assert r.status_code == 422, r.text
    assert "real interactor" in r.json()["detail"]


def test_a_ring_from_another_desk_cannot_seed_a_session(client):
    """A session may cite the bell that started it, but only its own desk's
    bell — a queue is not transferable."""
    desk_a, desk_b = _desk(client), _desk(client, display_name="Other")
    caller = _caller(client)
    ring = client.post(f"/desks/{desk_b['id']}/bell",
                       json={"note": "hello"}).json()
    r = client.post(f"/desks/{desk_a['id']}/sessions",
                    json={"caller_id": caller["id"],
                          "ring_id": ring["ring_id"]},
                    headers=_bearer(desk_a["desk_token"]))
    assert r.status_code == 422, r.text
    assert "not this desk's" in r.json()["detail"]


# --- an offer is not access -------------------------------------------------

def test_an_offer_grants_nothing(client):
    """The row is born `offered` and carries no token — to either party."""
    desk, caller, dh, ch, sess = _counter(client)
    r = client.post(f"/desk-sessions/{sess['id']}/connections",
                    json={"kind": "screen_share", "target": "Vera's laptop"},
                    headers=dh)
    assert r.status_code == 201, r.text
    offered = r.json()
    assert offered["status"] == "offered"
    assert "token" not in offered
    for head in (dh, ch):
        view = client.get(f"/desk-sessions/{sess['id']}", headers=head).json()
        assert "token" not in view["connections"][0]


def test_only_the_desk_offers_and_only_the_caller_answers(client):
    desk, caller, dh, ch, sess = _counter(client)
    r = client.post(f"/desk-sessions/{sess['id']}/connections",
                    json={"kind": "screen_share", "target": "laptop"},
                    headers=ch)
    assert r.status_code == 403, r.text
    cid = client.post(f"/desk-sessions/{sess['id']}/connections",
                      json={"kind": "screen_share", "target": "laptop"},
                      headers=dh).json()["id"]
    r = client.post(f"/desk-sessions/{sess['id']}/connections/{cid}/answer",
                    json={"accept": True}, headers=dh)
    assert r.status_code == 403, r.text
    assert "their machine" in r.json()["detail"]


def test_a_stranger_is_no_party_at_all(client):
    desk, caller, dh, ch, sess = _counter(client)
    stranger = _caller(client)
    r = client.get(f"/desk-sessions/{sess['id']}",
                   headers=_bearer(stranger["token"]))
    assert r.status_code == 403, r.text


def test_remote_control_needs_a_written_scope(client):
    """Driving somebody's machine under "whatever needs doing" is how a
    repair story becomes a horror story."""
    desk, caller, dh, ch, sess = _counter(client)
    r = client.post(f"/desk-sessions/{sess['id']}/connections",
                    json={"kind": "remote_control", "target": "Vera's PC"},
                    headers=dh)
    assert r.status_code == 422, r.text
    assert "scope" in r.json()["detail"]
    r = client.post(f"/desk-sessions/{sess['id']}/connections",
                    json={"kind": "remote_control", "target": "Vera's PC",
                          "scope": "printer driver reinstall only"},
                    headers=dh)
    assert r.status_code == 201, r.text


def test_every_offer_says_what_it_means_in_words(client):
    """The sentence the caller agrees to travels with the offer, from the
    same table the code enforces — not re-written by each client."""
    desk, caller, dh, ch, sess = _counter(client)
    o = client.post(f"/desk-sessions/{sess['id']}/connections",
                    json={"kind": "app_access", "target": "QuickBooks"},
                    headers=dh).json()
    assert o["means"] == ("they can use the named program on your behalf "
                          "for this session")


# --- accept mints, end kills ------------------------------------------------

def test_accept_mints_the_token_for_the_caller_alone(client):
    desk, caller, dh, ch, sess = _counter(client)
    cid = client.post(f"/desk-sessions/{sess['id']}/connections",
                      json={"kind": "screen_share", "target": "laptop"},
                      headers=dh).json()["id"]
    accepted = client.post(
        f"/desk-sessions/{sess['id']}/connections/{cid}/answer",
        json={"accept": True}, headers=ch).json()
    assert accepted["status"] == "active"
    assert accepted["token"].startswith("dlk_")
    desk_view = client.get(f"/desk-sessions/{sess['id']}", headers=dh).json()
    assert "token" not in desk_view["connections"][0], (
        "the desk was handed the caller's link secret")
    caller_view = client.get(f"/desk-sessions/{sess['id']}",
                             headers=ch).json()
    assert caller_view["connections"][0]["token"] == accepted["token"]


def test_declined_stays_declined(client):
    desk, caller, dh, ch, sess = _counter(client)
    cid = client.post(f"/desk-sessions/{sess['id']}/connections",
                      json={"kind": "file_drop", "target": "photos"},
                      headers=dh).json()["id"]
    r = client.post(f"/desk-sessions/{sess['id']}/connections/{cid}/answer",
                    json={"accept": False}, headers=ch)
    assert r.json()["status"] == "declined"
    r = client.post(f"/desk-sessions/{sess['id']}/connections/{cid}/answer",
                    json={"accept": True}, headers=ch)
    assert r.status_code == 422, r.text


def test_either_side_can_end_and_the_token_dies_in_the_row(client):
    from qrme import db as qdb, desks as desks_mod
    for ender, head_key in (("caller", 3), ("desk", 2)):
        desk, caller, dh, ch, sess = _counter(client)
        heads = (None, None, dh, ch)
        cid = client.post(f"/desk-sessions/{sess['id']}/connections",
                          json={"kind": "screen_share", "target": "laptop"},
                          headers=dh).json()["id"]
        token = client.post(
            f"/desk-sessions/{sess['id']}/connections/{cid}/answer",
            json={"accept": True}, headers=ch).json()["token"]
        assert desks_mod.connection_token_live(token)
        r = client.post(f"/desk-sessions/{sess['id']}/connections/{cid}/end",
                        headers=heads[head_key])
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "ended"
        assert r.json()["ended_by"] == ender
        assert not desks_mod.connection_token_live(token)
        row = qdb.connect().execute(
            "SELECT token FROM desk_connections WHERE id=?",
            (cid,)).fetchone()
        assert row["token"] is None, (
            "the secret survived the end — NULLed is the contract")


def test_closing_the_session_ends_every_live_link(client):
    desk, caller, dh, ch, sess = _counter(client)
    ids = []
    for kind, target in (("screen_share", "laptop"),
                         ("app_access", "QuickBooks")):
        cid = client.post(f"/desk-sessions/{sess['id']}/connections",
                          json={"kind": kind, "target": target},
                          headers=dh).json()["id"]
        client.post(f"/desk-sessions/{sess['id']}/connections/{cid}/answer",
                    json={"accept": True}, headers=ch)
        ids.append(cid)
    closed = client.post(f"/desk-sessions/{sess['id']}/close",
                         headers=ch).json()
    assert closed["status"] == "closed" and closed["closed_by"] == "caller"
    assert all(c["status"] == "ended" for c in closed["connections"])
    r = client.post(f"/desk-sessions/{sess['id']}/connections",
                    json={"kind": "file_drop", "target": "x"}, headers=dh)
    assert r.status_code == 422, r.text


def test_the_caller_holds_their_own_history(client):
    desk, caller, dh, ch, sess = _counter(client)
    r = client.get(f"/interactors/{caller['id']}/desk-sessions", headers=ch)
    assert r.status_code == 200 and r.json()[0]["id"] == sess["id"]
    stranger = _caller(client)
    r = client.get(f"/interactors/{caller['id']}/desk-sessions",
                   headers=_bearer(stranger["token"]))
    assert r.status_code == 403, r.text


# --- the rated gate stands where it always stood ----------------------------

def test_on_a_rated_desk_a_minor_cannot_accept_a_connection(client):
    """The adult gate is on the card, the view, the bell and joining — and
    now on the accept, which is the deepest thing a caller can do."""
    desk, caller, dh, ch, sess = _counter(client, rated=True,
                                          birthdate="2010-01-01")
    cid = client.post(f"/desk-sessions/{sess['id']}/connections",
                      json={"kind": "screen_share", "target": "laptop"},
                      headers=dh).json()["id"]
    r = client.post(f"/desk-sessions/{sess['id']}/connections/{cid}/answer",
                    json={"accept": True}, headers=ch)
    assert r.status_code == 403, r.text
    assert "18+" in r.json()["detail"]


# --- the skill across the counter -------------------------------------------
#
# "Program access such as Cursor, and skills" — the desk's service is not only
# a live link. QRME already had a two-party skill-grant system (`sharing.py`)
# and a desk was already a surface it could ride; what was missing was the
# *program* as a lendable kind, and a counter session as a surface whose
# closing takes its grants with it. Both exist now, and the whole arc is
# driven here: lend a program on the session, use it, close the counter,
# and watch the permission die with the place that justified it.

def _staffer(client):
    """The person behind the counter, as themselves — the lender on a skill
    grant is a person, and an id in a body is a claim, so they authenticate
    with their own interactor token like anybody else."""
    r = client.post("/interactors", json={"display_name": "Marcus",
                                          "birthdate": "1970-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


def test_a_desk_can_lend_a_program_on_the_session(client):
    desk, caller, dh, ch, sess = _counter(client)
    staffer = _staffer(client)
    sh = _bearer(staffer["token"])
    r = client.post("/skill-grants", json={
        "lender_id": staffer["id"], "borrower_id": caller["id"],
        "surface": "desk_session", "surface_id": sess["id"],
        "skill_kind": "app", "skill_ref": "cursor",
        "title": "Cursor, driven through my connector for this repair"},
        headers=sh)
    assert r.status_code == 201, r.text
    grant = r.json()
    assert grant["state"] == "offered"
    r = client.post(f"/skill-grants/{grant['id']}/accept",
                    json={"actor_id": caller["id"]}, headers=ch)
    assert r.status_code == 200, r.text
    r = client.post(f"/skill-grants/{grant['id']}/use", json={
        "borrower_id": caller["id"], "what": "refactor the invoice script"},
        headers=ch)
    assert r.status_code == 201, r.text
    assert r.json()["skill_ref"] == "cursor"
    log = client.get(f"/skill-grants/{grant['id']}/uses", headers=sh).json()
    assert len(log["uses"]) == 1, log
    assert log["uses"][0]["what"] == "refactor the invoice script", log


def test_closing_the_counter_takes_its_lent_skills_with_it(client):
    """The same rule the live links obey. Exchanges and watch parties already
    close their grants when the place ends; a counter session that did not
    would leave "use Cursor for this repair" standing after the repair."""
    desk, caller, dh, ch, sess = _counter(client)
    staffer = _staffer(client)
    grant = client.post("/skill-grants", json={
        "lender_id": staffer["id"], "borrower_id": caller["id"],
        "surface": "desk_session", "surface_id": sess["id"],
        "skill_kind": "app", "skill_ref": "cursor",
        "title": "Cursor for this session"},
        headers=_bearer(staffer["token"])).json()
    client.post(f"/skill-grants/{grant['id']}/accept",
                json={"actor_id": caller["id"]}, headers=ch)
    client.post(f"/desk-sessions/{sess['id']}/close", headers=ch)
    r = client.post(f"/skill-grants/{grant['id']}/use", json={
        "borrower_id": caller["id"], "what": "one more thing"}, headers=ch)
    assert r.status_code == 422, (
        "the counter closed and the lent program still answered: " + r.text)
    state = client.get(f"/skill-grants/{grant['id']}", headers=ch).json()
    assert state["state"] == "closed", state
