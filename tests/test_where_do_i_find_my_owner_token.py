"""Signing in reaches what you own — the loop that was open.

    asked     where do I find my owner token
    mattered  the only route that lists a person's profiles asked for one
              first, and the only place one is ever handed out is the create
              response

An owner token is minted once, at profile creation, and given to whichever
client did the creating. `GET /profiles/{id}/siblings` — the roster — needs
one before it will list anything, and it is right to: it refuses to be keyed
on `owner_id` because *an id in a path is a string somebody chooses, not a
secret*. But that leaves the person who reinstalled, or who made the profile
on their phone and is now at the console, with no way to enumerate their own
profiles and no way to open one.

`GET /accounts/{id}/profiles` is the same roster reached through the
credential such a person does have — the account token behind an email and a
password. `POST /accounts/{id}/profiles/{pid}/owner-token` is the grant, kept
deliberately separate from the read.

Four ways this could be wrong, one guard each:

1. **It lists somebody else's profiles.** The path carries an account id, so
   the check that it matches the token is the whole of the isolation.
2. **The listing hands out capability.** A roster is a read. The moment a
   token rides along, every screen showing a person their profiles is also
   handing out control of them.
3. **The mint is an oracle.** A profile on another account must answer the
   same as a profile that does not exist.
4. **The mint is a rotation.** Recovering access on a laptop must not sign out
   the phone that has been holding a token for a year.
"""

from __future__ import annotations

from qrme import mailer


def _capture_mail(monkeypatch):
    sent: list[dict] = []
    monkeypatch.setattr(mailer, "deliver",
                        lambda to, subject, body: sent.append(
                            {"to": to, "subject": subject, "body": body})
                        or "smtp")
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    return sent


def _code_from(message: dict) -> str:
    import re
    m = re.search(r"code (?:is|in the app): (\d{6})", message["body"])
    assert m, message["body"]
    return m.group(1)


def _account(client, monkeypatch, email="dana@example.test") -> dict:
    """A verified account and its token."""
    sent = _capture_mail(monkeypatch)
    r = client.post("/signup", json={
        "email": email, "password": "hunter2-hunter2", "display_name": "Dana"})
    assert r.status_code == 201, r.text
    r = client.post("/verify-email",
                    json={"email": email, "code": _code_from(sent[-1])})
    assert r.status_code == 200, r.text
    return r.json()


def _profile(client, owner_id: str, name="Dana", kind="self") -> dict:
    r = client.post("/profiles", json={
        "owner_id": owner_id, "kind": kind, "display_name": name,
        "persona": "A retired teacher who loves gardening and dry humor.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(token: str) -> dict:
    return {"authorization": f"Bearer {token}"}


def test_signing_in_lists_what_this_account_holds(client, monkeypatch):
    me = _account(client, monkeypatch)
    first = _profile(client, me["account_id"], "Dana")
    second = _profile(client, me["account_id"], "Dana at work",
                      kind="fictional")

    r = client.get(f"/accounts/{me['account_id']}/profiles",
                   headers=_auth(me["account_token"]))
    assert r.status_code == 200, r.text
    body = r.json()
    ids = {p["profile_id"] for p in body["profiles"]}
    assert ids == {first["id"], second["id"]}
    assert body["count"] == 2
    # The kind travels, because a caller looking for the person's own profile
    # has no other way to tell which of these it is — JIM's link refuses
    # anything that is not `self`, and doing that after the person has already
    # chosen is a worse screen than not offering the choice.
    assert {p["kind"] for p in body["profiles"]} == {"self", "fictional"}


def test_the_roster_is_not_readable_by_another_account(client, monkeypatch):
    """Both directions, because a one-way check passes on a broken gate."""
    mine = _account(client, monkeypatch, "dana@example.test")
    theirs = _account(client, monkeypatch, "sam@example.test")
    _profile(client, mine["account_id"])

    assert client.get(f"/accounts/{mine['account_id']}/profiles",
                      headers=_auth(theirs["account_token"])
                      ).status_code == 403
    assert client.get(f"/accounts/{theirs['account_id']}/profiles",
                      headers=_auth(mine["account_token"])
                      ).status_code == 403
    assert client.get(
        f"/accounts/{mine['account_id']}/profiles").status_code == 401


def test_the_listing_carries_no_credential(client, monkeypatch):
    """A roster is a read. `qrme/dock.py` already says the rule in one line:
    nothing that authorises anything belongs on a surface."""
    me = _account(client, monkeypatch)
    _profile(client, me["account_id"])
    body = client.get(f"/accounts/{me['account_id']}/profiles",
                      headers=_auth(me["account_token"])).json()

    flat = repr(body)
    assert "owner_token" not in flat
    assert "token" not in flat


def test_the_owner_token_is_minted_on_request_and_works(client, monkeypatch):
    me = _account(client, monkeypatch)
    made = _profile(client, me["account_id"])

    r = client.post(
        f"/accounts/{me['account_id']}/profiles/{made['id']}/owner-token",
        headers=_auth(me["account_token"]))
    assert r.status_code == 201, r.text
    minted = r.json()["owner_token"]
    assert minted != made.get("owner_token")

    # It is the real capability, not a look-alike: the roster route that
    # refuses everything but an owner token opens with it.
    assert client.get(f"/profiles/{made['id']}/siblings",
                      headers=_auth(minted)).status_code == 200


def test_minting_does_not_retire_the_tokens_already_out_there(client,
                                                              monkeypatch):
    """The phone that created the profile keeps working.

    A rotation here would make recovering access on a laptop the button that
    silently unlinks somebody's Guardian — and nobody pressing this is asking
    for that. Revoking is a different intent with its own door.
    """
    me = _account(client, monkeypatch)
    made = _profile(client, me["account_id"])
    original = made["owner_token"]

    client.post(
        f"/accounts/{me['account_id']}/profiles/{made['id']}/owner-token",
        headers=_auth(me["account_token"]))

    assert client.get(f"/profiles/{made['id']}/siblings",
                      headers=_auth(original)).status_code == 200


def test_a_profile_on_another_account_answers_like_one_that_is_not_there(
        client, monkeypatch):
    """Same answer, or the route is a directory of which ids exist here."""
    mine = _account(client, monkeypatch, "dana@example.test")
    theirs = _account(client, monkeypatch, "sam@example.test")
    not_mine = _profile(client, theirs["account_id"], "Sam")

    real = client.post(
        f"/accounts/{mine['account_id']}/profiles/{not_mine['id']}/owner-token",
        headers=_auth(mine["account_token"]))
    absent = client.post(
        f"/accounts/{mine['account_id']}/profiles/prf_nothing/owner-token",
        headers=_auth(mine["account_token"]))
    assert real.status_code == absent.status_code == 404
    assert real.json()["detail"] == absent.json()["detail"]


def test_the_mint_needs_this_accounts_own_token(client, monkeypatch):
    mine = _account(client, monkeypatch, "dana@example.test")
    theirs = _account(client, monkeypatch, "sam@example.test")
    made = _profile(client, mine["account_id"])

    assert client.post(
        f"/accounts/{mine['account_id']}/profiles/{made['id']}/owner-token",
        headers=_auth(theirs["account_token"])).status_code == 403
    assert client.post(
        f"/accounts/{mine['account_id']}/profiles/{made['id']}/owner-token"
    ).status_code == 401
    # And an owner token is not an account token: holding the profile does not
    # make you the account, which is what keeps the roster off this door.
    assert client.post(
        f"/accounts/{mine['account_id']}/profiles/{made['id']}/owner-token",
        headers=_auth(made["owner_token"])).status_code == 403


def test_a_password_reset_closes_the_door_again(client, monkeypatch):
    """The account token is the key to this pair, so it must die with the
    password — otherwise a reset that revokes every session leaves the one
    session that can mint fresh owner tokens standing."""
    me = _account(client, monkeypatch)
    _profile(client, me["account_id"])

    # A fresh recorder, after the account exists: `_account` installs its own,
    # and the earlier list stops receiving the moment it does.
    sent = _capture_mail(monkeypatch)
    client.post("/password/reset/request", json={"email": "dana@example.test"})
    code = _code_from(sent[-1])
    r = client.post("/password/reset", json={
        "email": "dana@example.test", "code": code,
        "new_password": "another-long-one"})
    assert r.status_code == 200, r.text

    assert client.get(f"/accounts/{me['account_id']}/profiles",
                      headers=_auth(me["account_token"])).status_code == 401
