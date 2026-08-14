"""A starter remembered you until you picked up your phone.

Memory works, and it always did: the chat route pulls the last turns for
(profile, interactor) and `remembrance` folds down everything older, so a
starter you have talked to for an hour opens the next conversation knowing
what you said. The keying is the whole mechanism.

And an interactor was minted per device and kept in that browser's local
storage, with no column tying it to an account. So the profile remembered a
*browser*. Same account, same human, second device — and Dr. Osei had never
met you.

    asked     does the profile remember the conversation
    mattered  does it remember the person
"""

from __future__ import annotations

import pytest

from qrme import accounts, db


@pytest.fixture()
def verified(client):
    """An account that can sign in, on a deployment with no mail transport —
    which activates locally, the path the packaged desktop app takes."""
    made = accounts.signup("sam@example.test", "a-good-password", "Sam")
    assert made.get("verified"), made
    return "sam@example.test", "a-good-password"


def test_signing_in_hands_back_the_same_person_every_time(client, verified):
    """Idempotent, or the fix reintroduces the defect with extra steps: a
    second sign-in producing a second interactor is a stranger again."""
    email, password = verified
    first = accounts.signin(email, password)
    second = accounts.signin(email, password)
    assert first["interactor_id"] == second["interactor_id"]
    assert first["interactor_id"].startswith("usr_")


def test_two_devices_are_one_person(client, verified, profile_id):
    """The defect, directly. Talk on one device, sign in on another, and the
    profile is talking to somebody it has met."""
    email, password = verified
    desktop = accounts.signin(email, password)["interactor_id"]
    said = client.post(f"/profiles/{profile_id}/chat",
                       json={"interactor_id": desktop,
                             "message": "I have a torn rotator cuff"})
    assert said.status_code == 200, said.text

    # A different device: nothing carried over but the email and password.
    phone = accounts.signin(email, password)["interactor_id"]
    assert phone == desktop
    seen = db.connect().execute(
        "SELECT COUNT(*) n FROM messages WHERE profile_id=? AND interactor_id=?",
        (profile_id, phone)).fetchone()["n"]
    assert seen == 2, "the second device sees the first device's conversation"


def test_a_stranger_who_signs_in_keeps_what_they_already_said(
        client, verified, profile_id):
    """The upgrade path, and the reason it matters.

    Somebody talks to three starters as a stranger, then makes an account.
    Minting a fresh person at that moment would make the account the exact
    moment their history was deleted."""
    email, password = verified
    stranger = client.post("/interactors",
                           json={"display_name": "Sam",
                                 "birthdate": "1990-02-02"}).json()["id"]
    client.post(f"/profiles/{profile_id}/chat",
                json={"interactor_id": stranger,
                      "message": "my shoulder has been bad for a month"})

    signed = accounts.signin(email, password,
                             adopt_interactor_id=stranger)
    assert signed["interactor_id"] == stranger
    kept = db.connect().execute(
        "SELECT COUNT(*) n FROM messages WHERE profile_id=? AND interactor_id=?",
        (profile_id, stranger)).fetchone()["n"]
    assert kept == 2, "the conversation survived getting an account"


def test_nobody_adopts_somebody_elses_person(client, verified):
    """An unattached interactor is a device's; one with an account is a
    person's, and moving it hands one person's remembered conversations to
    another."""
    email, password = verified
    mine = accounts.signin(email, password)["interactor_id"]
    accounts.signup("rae@example.test", "another-good-password", "Rae")
    with pytest.raises(accounts.AccountError) as caught:
        accounts.signin("rae@example.test", "another-good-password",
                        adopt_interactor_id=mine)
    assert caught.value.status == 403


def test_adopting_a_person_who_does_not_exist_says_so(client, verified):
    email, password = verified
    with pytest.raises(accounts.AccountError) as caught:
        accounts.signin(email, password, adopt_interactor_id="usr_nobody")
    assert caught.value.status == 404


def test_a_visitor_with_no_account_still_gets_remembered(client, profile_id):
    """Nullable is not a shortcut. A stranger scanning a beacon has no
    account and still gets a conversation, and still gets it remembered for
    as long as their device holds the id. Binding is what an account adds,
    not what a conversation requires."""
    stranger = client.post("/interactors",
                           json={"display_name": "Passer-by",
                                 "birthdate": "1990-02-02"}).json()["id"]
    for line in ("what do you do", "and what did I just ask"):
        assert client.post(f"/profiles/{profile_id}/chat",
                           json={"interactor_id": stranger,
                                 "message": line}).status_code == 200
    row = db.connect().execute("SELECT account_id FROM interactors WHERE id=?",
                               (stranger,)).fetchone()
    assert row["account_id"] is None
    kept = db.connect().execute(
        "SELECT COUNT(*) n FROM messages WHERE profile_id=? AND interactor_id=?",
        (profile_id, stranger)).fetchone()["n"]
    assert kept == 4


def test_the_person_arrives_with_a_token_to_speak_as(client, verified):
    """An id with no token is a name a client cannot sign as — the chat route
    takes the interactor's own token, so handing back one without the other
    would be a door with no key."""
    email, password = verified
    signed = accounts.signin(email, password)
    assert signed["interactor_token"]
    assert signed["interactor_token"] != signed["account_token"]
