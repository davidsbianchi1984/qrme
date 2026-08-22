import os

import pytest
from fastapi.testclient import TestClient

from qrme import db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "test.db"))
    monkeypatch.setenv("QRME_LLM", "stub")
    db.reset()
    from qrme.api import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
    db.reset()


ADULT_VERIFICATION = {"birthdate": "1984-06-01"}


@pytest.fixture()
def profile_id(client):
    response = client.post(
        "/profiles",
        json={
            "owner_id": "owner-1",
            "kind": "self",
            "display_name": "Dana",
            "persona": "A retired teacher who loves gardening and dry humor.",
            "verification": ADULT_VERIFICATION,
            # Pro, where the product default is Basic — see the note on
            # tests/test_capabilities.py:make_profile. The membership gate is
            # tested on its own accounts in test_tiers.py.
            "plan": "pro",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    # Authenticate the client as this profile's owner for owner-only endpoints.
    client.headers["authorization"] = f"Bearer {body['owner_token']}"
    return body["id"]


@pytest.fixture()
def interactor_id(client):
    """Sam — an ordinary signed-in person, with an account and a plan.

    The account is not decoration. A memory of a conversation belongs to
    the **person** now rather than to the profile they were talking to, so
    whether one is kept is a fact about *their* plan. Sam without an
    account is a visitor, and a visitor's turn is not sealed into a vault
    nobody holds a key to.

    This fixture used to make an accountless interactor, and every memory
    test still passed — because the gate asked about the profile OWNER's
    plan, so a signed-out stranger's words were kept in the member's vault.
    The fixture agreeing with the product is the point: use
    `visitor_interactor` for somebody who really has not signed in.
    """
    response = client.post(
        "/interactors",
        json={"display_name": "Sam", "birthdate": "2000-01-15"},
    )
    assert response.status_code == 201, response.text
    who = response.json()["id"]
    enrol(who)
    return who


@pytest.fixture()
def visitor_interactor(client):
    """Somebody talking to a profile without signing in.

    No account, so no plan, so nowhere of their own for a memory to live.
    Deliberately separate from `interactor_id` so a test that means
    "signed out" has to say so.
    """
    response = client.post(
        "/interactors",
        json={"display_name": "Wren", "birthdate": "1996-07-02"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture()
def interactor_head(client, interactor_id):
    """Sam's own token, as a header.

    Separate from `interactor_id` so a test has to reach for it deliberately.
    Several surfaces about a person — their rating, their engagement record —
    were readable and writable with no token at all, and the tests did not
    notice because they had none to send.
    """
    row = client.get(f"/interactors/{interactor_id}")
    if row.status_code == 200 and row.json().get("token"):
        return {"authorization": f"Bearer {row.json()['token']}"}
    from qrme import auth
    return {"authorization": f"Bearer {auth.issue('interactor', interactor_id)}"}

def enrol(interactor_id: str, plan: str = "pro") -> str:
    """Give this person an account on a plan, and hand back the account id.

    A memory of a conversation belongs to the **person** now, not to the
    profile they were talking to, so whether one is kept is a fact about
    *their* plan. An interactor with no account behind it is a visitor, and
    a visitor's turn is not sealed into a vault nobody holds a key to.

    That is a real change in who gets remembered, and it is why so many
    tests reach for this: they were written when the gate asked about the
    profile owner, so a signed-out stranger talking to a paying member's
    profile had their words kept in the member's vault. Tests that want a
    memory now have to say whose it is.
    """
    from qrme import db, tiers

    account = f"acct-{interactor_id}"
    tiers.subscribe(account, plan)
    conn = db.connect()
    conn.execute("UPDATE interactors SET account_id=? WHERE id=?",
                 (account, interactor_id))
    conn.commit()
    return account


@pytest.fixture()
def paying_interactor(client, interactor_id):
    """`interactor_id`, enrolled — the ordinary signed-in person."""
    enrol(interactor_id)
    return interactor_id
