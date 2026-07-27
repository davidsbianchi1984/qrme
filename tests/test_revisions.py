"""Editing and retracting something you already said.

The point of the feature is that the correction carries forward: what somebody
said is what the profile reasons from next turn, so a typo does not just look
untidy, it becomes something the profile believes. The tests below hold the
edges — you cannot rewrite the other side, an edit cannot smuggle past
moderation, and a reply written before an edit says so.
"""

import pytest

from qrme import db, revisions
from tests.test_capabilities import auth_header, make_interactor, make_profile


def _exchange(client, profile, interactor_id, text="What year was that?"):
    r = client.post(f"/profiles/{profile['id']}/chat",
                    json={"interactor_id": interactor_id, "message": text})
    assert r.status_code in (200, 201), r.text
    rows = db.connect().execute(
        "SELECT id, role FROM messages WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at, rowid", (profile["id"], interactor_id)
    ).fetchall()
    mine = [r["id"] for r in rows if r["role"] == "interactor"]
    theirs = [r["id"] for r in rows if r["role"] != "interactor"]
    return mine, theirs


# -- editing your own turn ---------------------------------------------------

def test_an_edit_replaces_what_you_said(client):
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    mine, _ = _exchange(client, p, who)

    r = client.patch(f"/profiles/{p['id']}/messages/{mine[0]}",
                     json={"interactor_id": who, "content": "What year, roughly?"},
                     headers=auth_header(p))
    assert r.status_code == 200, r.text
    assert r.json()["content"] == "What year, roughly?"
    assert r.json()["edited"] is True


def test_the_correction_is_what_the_next_turn_reasons_from(client):
    """The whole point. History is rebuilt from these rows on every turn, so
    the edited text is simply what the next prompt sees — nothing to reindex,
    no snapshot to go stale."""
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    mine, _ = _exchange(client, p, who, "I was born in 1885.")
    client.patch(f"/profiles/{p['id']}/messages/{mine[0]}",
                 json={"interactor_id": who, "content": "I was born in 1985."},
                 headers=auth_header(p))

    history = db.connect().execute(
        "SELECT content FROM messages WHERE profile_id=? AND interactor_id=?"
        " AND status='approved' AND role='interactor'", (p["id"], who)
    ).fetchall()
    joined = " ".join(h["content"] for h in history)
    assert "1985" in joined and "1885" not in joined


def test_the_previous_wording_is_kept_as_a_revision(client):
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    mine, _ = _exchange(client, p, who, "First try.")
    client.patch(f"/profiles/{p['id']}/messages/{mine[0]}",
                 json={"interactor_id": who, "content": "Second try."},
                 headers=auth_header(p))

    revs = revisions.revisions(mine[0])
    assert revs[0]["was"] == "First try."
    assert revs[0]["became"] == "Second try."


# -- what you cannot edit ----------------------------------------------------

def test_you_cannot_rewrite_the_profiles_reply(client):
    """The one edit that must never be possible. Putting words in a synthetic
    person's mouth is fabrication, not editing — and on this platform that is
    the whole thing being guarded."""
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    _, theirs = _exchange(client, p, who)
    assert theirs, "expected the profile to have replied"

    r = client.patch(f"/profiles/{p['id']}/messages/{theirs[0]}",
                     json={"interactor_id": who, "content": "I promise you a refund."},
                     headers=auth_header(p))
    assert r.status_code == 422
    assert "not yours to rewrite" in r.json()["detail"]


def test_you_cannot_edit_somebody_elses_message(client):
    p = make_profile(client, display_name="Listener")
    a = make_interactor(client, name="Ada")
    b = make_interactor(client, name="Bo", birthdate="1990-02-02")
    mine, _ = _exchange(client, p, a)

    with pytest.raises(revisions.RevisionError):
        revisions.edit(mine[0], "not mine", b)


def test_an_edit_is_moderated_like_a_fresh_message(client):
    """Otherwise the edit box is a way past a filter the original had to clear:
    post something harmless, then change it to what you meant."""
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    mine, _ = _exchange(client, p, who, "Hello there.")

    client.patch(f"/profiles/{p['id']}/messages/{mine[0]}",
                 json={"interactor_id": who, "content": "kill yourself"},
                 headers=auth_header(p))
    row = db.connect().execute("SELECT status FROM messages WHERE id=?",
                               (mine[0],)).fetchone()
    assert row["status"] == "rejected"
    # And a rejected turn does not reach the next prompt.
    approved = db.connect().execute(
        "SELECT COUNT(*) AS n FROM messages WHERE id=? AND status='approved'",
        (mine[0],)).fetchone()["n"]
    assert approved == 0


# -- retraction --------------------------------------------------------------

def test_retracting_stops_the_text_counting_without_deleting_the_row(client):
    """The moderation trail is why a blocked message is kept at all; a
    retraction that erased the row would be a way to remove one."""
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    mine, _ = _exchange(client, p, who, "Forget I said this.")

    r = client.request("DELETE", f"/profiles/{p['id']}/messages/{mine[0]}",
                       json={"interactor_id": who}, headers=auth_header(p))
    assert r.status_code == 200, r.text
    row = db.connect().execute("SELECT status FROM messages WHERE id=?",
                               (mine[0],)).fetchone()
    assert row is not None                      # the row survives
    assert row["status"] == "retracted"         # but is not 'approved'


def test_a_retracted_turn_leaves_the_prompt(client):
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    mine, _ = _exchange(client, p, who, "A thing I regret.")
    revisions.retract(mine[0], who)

    approved = db.connect().execute(
        "SELECT content FROM messages WHERE profile_id=? AND interactor_id=?"
        " AND status='approved' AND role='interactor'", (p["id"], who)
    ).fetchall()
    assert "A thing I regret." not in [a["content"] for a in approved]


def test_you_cannot_retract_the_profiles_reply(client):
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    _, theirs = _exchange(client, p, who)
    with pytest.raises(revisions.RevisionError):
        revisions.retract(theirs[0], who)


# -- the honest part ---------------------------------------------------------

def test_a_reply_written_before_an_edit_is_flagged_stale(client):
    """The answer under a corrected question was a response to the old
    wording. Leaving it unmarked implies the profile answered the new one."""
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    mine, theirs = _exchange(client, p, who, "How old is it?")
    assert theirs

    client.patch(f"/profiles/{p['id']}/messages/{mine[0]}",
                 json={"interactor_id": who, "content": "How old is she?"},
                 headers=auth_header(p))

    entries = client.get(f"/profiles/{p['id']}/thread/{who}",
                         headers=auth_header(p)).json()["messages"]
    reply = [e for e in entries if e["id"] == theirs[0]][0]
    assert reply["answers_stale_text"] is True
    assert "answered the earlier wording" in reply["stale_note"]


def test_an_unedited_conversation_flags_nothing(client):
    p = make_profile(client, display_name="Listener")
    who = make_interactor(client)
    _exchange(client, p, who)
    entries = client.get(f"/profiles/{p['id']}/thread/{who}",
                         headers=auth_header(p)).json()["messages"]
    assert entries
    assert not any(e["answers_stale_text"] for e in entries)
    assert not any(e["edited"] for e in entries)
