"""Development mode means localhost, not everybody.

`auth.require_reviewer` guards the two most destructive operations in the
product. Upholding an objection **terminates a profile and erases its
content**; succession **hands a profile to a different owner**. Both sit
outside profile ownership on purpose — an owner must not adjudicate an
objection against their own profile — so the gate is a deployment secret,
`QRME_ADMIN_TOKEN`.

With that variable unset the function used to `return` unconditionally, for
any caller from any address, while its own docstring said "for local use
only". Nothing enforced the local part. It also claimed to match "PDI's admin
convention", and the cloud gateway's version of that convention had a
localhost check the whole time:

    if not configured:
        host = request.client.host if request.client else ""
        if host in _LOCAL_CALLERS:
            return "local-dev"
        raise HTTPException(503, ...)

Two things make this worth a file rather than a line in a changelog.

**It failed open on the deployment least able to notice.** An operator who
configured the token was fine. An operator who did not — a first deployment, a
staging box that got a public address, anybody following a quickstart — was
handing anonymous callers the ability to erase profiles.

**The docstring was the bug.** The code did what it said in every respect
except the one that mattered, so reading it carefully produced false
confidence. That is the same shape as a validator whose error message promises
more than its pattern checks, and it is worth naming as a shape because
reviewing the sentence is exactly how somebody would have concluded it was
fine.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from qrme import auth


class _Client:
    def __init__(self, host):
        self.host = host


class _Request:
    """Only what `require_reviewer` reads: a peer address and headers."""

    def __init__(self, host, token=None):
        self.client = _Client(host) if host is not None else None
        self.headers = {"authorization": f"Bearer {token}"} if token else {}


@pytest.mark.parametrize("host", sorted(auth._LOCAL_CALLERS))
def test_a_local_caller_still_gets_development_mode(host, monkeypatch):
    """The convenience the mode exists for is preserved."""
    monkeypatch.delenv("QRME_ADMIN_TOKEN", raising=False)
    auth.require_reviewer(_Request(host))     # no exception


@pytest.mark.parametrize("host", ["203.0.113.7", "10.0.0.4", "::ffff:8.8.8.8"])
def test_a_remote_caller_is_refused_when_no_token_is_configured(host, monkeypatch):
    """The half that was missing. 503, not 200."""
    monkeypatch.delenv("QRME_ADMIN_TOKEN", raising=False)
    with pytest.raises(HTTPException) as caught:
        auth.require_reviewer(_Request(host))
    assert caught.value.status_code == 503
    # Name the variable, so the operator can act on the refusal rather than
    # only learn that something is closed.
    assert "QRME_ADMIN_TOKEN" in caught.value.detail


def test_a_caller_with_no_peer_address_is_refused(monkeypatch):
    """`request.client` can be None. Absent is not local."""
    monkeypatch.delenv("QRME_ADMIN_TOKEN", raising=False)
    with pytest.raises(HTTPException) as caught:
        auth.require_reviewer(_Request(None))
    assert caught.value.status_code == 503


def test_a_configured_token_still_gates_by_the_token(monkeypatch):
    """Configuring the variable must not have been quietly weakened into an
    address check — the address only decides what *unset* means."""
    monkeypatch.setenv("QRME_ADMIN_TOKEN", "s3cret")
    # Local, but wrong token: still refused. Being nearby is not being trusted.
    with pytest.raises(HTTPException) as wrong:
        auth.require_reviewer(_Request("127.0.0.1", token="guess"))
    assert wrong.value.status_code == 403
    with pytest.raises(HTTPException) as none:
        auth.require_reviewer(_Request("127.0.0.1"))
    assert none.value.status_code == 401
    # Remote with the right token: allowed. That is what the token is for.
    auth.require_reviewer(_Request("203.0.113.7", token="s3cret"))


def test_the_owner_path_still_works_behind_the_stricter_gate(client):
    """`_require_owner_or_reviewer` tries the reviewer first and falls back to
    the owner when it raises.

    Worth asserting rather than assuming: the fallback is written as
    `except HTTPException`, so making the reviewer check raise in a new case
    changes which branch a real request takes. An owner reading their own
    case must still get through.
    """
    from qrme.routers import governance

    p = client.post("/profiles", json={
        "owner_id": "acct_gate", "kind": "other_person",
        "display_name": "Depicted", "purpose": "family",
        "persona": "a neighbour",
        "verification": {"birthdate": "1980-02-02"},
        "consent": {"basis": "subject_consent", "attestor": "the subject"},
    }).json()
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "case-1", "reason": "not me",
    }).json()
    r = client.get(f"/objections/{obj['id']}/audit",
                   headers={"authorization": f"Bearer {p['owner_token']}"})
    assert r.status_code == 200, r.text
    assert r.json()["audit_events"], "the owner cannot read their own case"
    assert governance is not None
