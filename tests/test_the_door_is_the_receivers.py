"""The open door: the receiver's standing yes to unprompted reach.

The oldest still-open ask — "somebody subscribing to the agent, rather
than the agent reaching them" — and the direction of consent flips.
What stood before was throttles: quiet hours, a rate cap, awaiting-
reply. Real protections, none of them a yes. Now the yes exists, it is
the receiver's alone, and every promise below is about whose hand is
on the handle.
"""

from __future__ import annotations

from qrme import opendoor

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile)
from tests.test_four_refusals_and_two_are_yours import _cast  # noqa: F401


def test_yours_to_open_and_yours_alone(client):
    p = make_profile(client, interaction_scope="proactive")
    user = make_interactor(client)
    stranger = make_interactor(client, "Sol", "1991-01-01")
    # The stranger's token cannot open somebody else's door.
    r = client.put(f"/interactors/{user}/open-door/{p['id']}",
                   headers=as_interactor(stranger),
                   json={"hear_first": True})
    assert r.status_code in (401, 403), (
        "somebody else opened this person's door")
    ok = client.put(f"/interactors/{user}/open-door/{p['id']}",
                    headers=as_interactor(user),
                    json={"hear_first": True, "cadence": "weekly"})
    assert ok.status_code == 200, ok.text
    assert ok.json()["open"] is True


def test_closing_keeps_the_record(client):
    p = make_profile(client)
    user = make_interactor(client)
    opendoor.set_door(user, p["id"], open_=True)
    closed = opendoor.set_door(user, p["id"], open_=False)
    assert closed["open"] is False
    assert closed["ever_opened"] is True and closed["closed_at"], (
        "a yes withdrawn became a yes never given — the record is gone")


def test_the_cadence_slows_a_profile_and_never_speeds_one(client):
    """max(owner's cap, door's cadence): a weekly door binds a daily
    profile; a daily door cannot hurry a weekly one."""
    from datetime import datetime, timedelta, timezone
    from qrme import db
    p, head, uid, _ = _cast(client, "acct_cadence", interval=0)
    opendoor.set_door(uid, p["id"], open_=True, cadence="weekly")
    assert client.post(f"/profiles/{p['id']}/proactive/{uid}",
                       headers=head).status_code == 200
    # Two days pass and the person replied — a 0h profile would go again,
    # and the weekly door says not yet.
    past = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    conn = db.connect()
    conn.execute("UPDATE proactive_state SET last_outreach_at=?,"
                 " awaiting_reply=0 WHERE profile_id=? AND interactor_id=?",
                 (past, p["id"], uid))
    conn.commit()
    r = client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    assert r.status_code == 429 and "168h" in r.json()["detail"], (
        "the door's pace did not bind — a subscription that cannot slow "
        "the reach is not consent, it is decoration")


def test_the_owner_reads_who_asked_and_nobody_else_does(client):
    p = make_profile(client, interaction_scope="proactive")
    user = make_interactor(client)
    opendoor.set_door(user, p["id"], open_=True)
    stranger = make_interactor(client, "Nia", "1992-01-01")
    bare = client.get(f"/profiles/{p['id']}/open-doors",
                      headers=as_interactor(stranger))
    assert bare.status_code in (401, 403), (
        "who subscribed to a profile is readable by somebody who is "
        "not its owner")
    from tests.test_capabilities import as_owner
    as_owner(client, p)
    mine = client.get(f"/profiles/{p['id']}/open-doors")
    assert mine.status_code == 200
    assert any(o["interactor_id"] == user
               for o in mine.json()["openers"])


def test_an_open_door_does_not_move_a_reactive_profile(client):
    """A subscription is not a lever on somebody else's profile: the
    owner's scope still decides whether the profile speaks first."""
    p = make_profile(client)          # reactive
    user = make_interactor(client)
    opendoor.set_door(user, p["id"], open_=True)
    r = client.post(f"/profiles/{p['id']}/proactive/{user}")
    assert r.status_code == 403
    assert "reactive-only" in r.json()["detail"]


def test_the_refusal_speaks_ten_languages():
    from qrme import i18n
    for lang in ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"):
        assert i18n.tr_public(opendoor.DOOR_CLOSED, lang) \
            != opendoor.DOOR_CLOSED, f"the door refusal is English in {lang}"
