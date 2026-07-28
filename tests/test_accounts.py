"""Email + password accounts: the address is verified before sign-in works.

QRME's shape: the account is what owns — its id is the ``owner_id`` profiles
are created under — while each profile keeps its own owner capability token.
Codes are hashed at rest, single-use, expiring; unknown-address and
wrong-password answers are indistinguishable; a signup code cannot reset a
password.
"""

from __future__ import annotations

from qrme import accounts, db, mailer


def _capture_mail(monkeypatch):
    """Swap the mail transport for a recorder — and report it as SMTP, so the
    email-proof flow is exercised (a console transport activates directly:
    no inbox can be proven where no mail can be sent)."""
    sent: list[dict] = []

    def fake_deliver(to, subject, body):
        sent.append({"to": to, "subject": subject, "body": body})
        return "smtp"

    monkeypatch.setattr(mailer, "deliver", fake_deliver)
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    return sent


def _code_from(message: dict) -> str:
    import re

    m = re.search(r"code (?:is|in the app): (\d{6})", message["body"])
    if not m:
        raise AssertionError(f"no code in {message['body']!r}")
    return m.group(1)


def _link_token_from(message: dict) -> str:
    import re

    m = re.search(r"token=([A-Za-z0-9_\-]+)", message["body"])
    if not m:
        raise AssertionError(f"no verify link in {message['body']!r}")
    return m.group(1)


def _signup(client, email="dana@example.test", password="hunter2-hunter2"):
    return client.post("/signup", json={
        "email": email, "password": password, "display_name": "Dana"})


def _verified(client, sent):
    _signup(client)
    r = client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[0])})
    assert r.status_code == 200, r.text
    return r.json()


def test_signup_sends_a_code_and_cannot_sign_in_yet(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    r = _signup(client)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["verified"] is False and body["code_delivery"] == "smtp"
    assert "account_token" not in body and "code" not in body
    assert len(sent) == 1 and sent[0]["to"] == "dana@example.test"
    assert client.post("/signin", json={
        "email": "dana@example.test",
        "password": "hunter2-hunter2"}).status_code == 403


def test_the_code_mints_the_first_session_and_the_account_owns_profiles(
        client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    acct = _verified(client, sent)
    assert acct["account_token"]
    # The account id is the owner_id a profile is created under; the profile
    # still mints its own owner token exactly as before.
    r = client.post("/profiles", json={
        "owner_id": acct["account_id"], "kind": "fictional",
        "display_name": "Marisol", "persona": "A warm chef.",
        "verification": {"birthdate": "1970-05-14"}, "terms_consent": True,
    })
    assert r.status_code == 201, r.text
    assert r.json()["owner_id"] == acct["account_id"]
    assert r.json()["owner_token"]


def test_a_wrong_code_verifies_nothing(client, monkeypatch):
    _capture_mail(monkeypatch)
    _signup(client)
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": "000000"}).status_code == 403


def test_a_code_is_single_use(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    code = _code_from(sent[0])
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": code}).status_code == 200
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": code}).status_code == 409


def test_resend_retires_the_previous_code(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    old = _code_from(sent[0])
    assert client.post("/verify-email/resend",
                       json={"email": "dana@example.test"}).status_code == 200
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": old}).status_code == 403
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[1])}
    ).status_code == 200


def test_wrong_password_and_unknown_address_answer_identically(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _verified(client, sent)
    wrong = client.post("/signin", json={
        "email": "dana@example.test", "password": "not-the-password"})
    unknown = client.post("/signin", json={
        "email": "nobody@example.test", "password": "whatever-here"})
    assert wrong.status_code == unknown.status_code == 403
    assert wrong.json()["detail"] == unknown.json()["detail"]


def test_forgot_password_resets_via_emailed_code(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _verified(client, sent)
    assert client.post("/password/reset/request", json={
        "email": "dana@example.test"}).status_code == 200
    assert "reset code is:" in sent[-1]["body"]
    r = client.post("/password/reset", json={
        "email": "dana@example.test", "code": _code_from(sent[-1]),
        "new_password": "a-brand-new-passphrase"})
    assert r.status_code == 200, r.text
    assert client.post("/signin", json={
        "email": "dana@example.test",
        "password": "hunter2-hunter2"}).status_code == 403
    assert client.post("/signin", json={
        "email": "dana@example.test",
        "password": "a-brand-new-passphrase"}).status_code == 200


def test_a_verify_code_cannot_reset_a_password(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    signup_code = _code_from(sent[0])
    client.post("/verify-email", json={
        "email": "dana@example.test", "code": signup_code})
    assert client.post("/password/reset", json={
        "email": "dana@example.test", "code": signup_code,
        "new_password": "a-brand-new-passphrase"}).status_code == 403


def test_neither_oracle_endpoint_reveals_who_has_an_account(client, monkeypatch):
    _capture_mail(monkeypatch)
    for path in ("/verify-email/resend", "/password/reset/request"):
        r = client.post(path, json={"email": "nobody@example.test"})
        assert r.status_code == 200
        assert r.json()["code_delivery"] == "none"


def test_passwords_and_codes_are_never_stored_in_the_clear(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    code = _code_from(sent[0])
    row = db.connect().execute(
        "SELECT * FROM accounts WHERE email='dana@example.test'").fetchone()
    assert "hunter2-hunter2" not in (row["password_hash"] + row["salt"])
    stored = db.connect().execute(
        "SELECT code_hash FROM email_codes").fetchall()
    assert all(code != r["code_hash"] for r in stored)


def test_the_emailed_link_verifies_and_the_app_notices_by_signing_in(
        client, monkeypatch):
    """The mail leads with a clickable link; the click lands in a browser and
    the app continues by signing in with the credentials it already holds."""
    sent = _capture_mail(monkeypatch)
    _signup(client)
    token = _link_token_from(sent[0])
    assert client.post("/signin", json={
        "email": "dana@example.test",
        "password": "hunter2-hunter2"}).status_code == 403
    r = client.get(f"/verify-email/click?token={token}")
    assert r.status_code == 200
    assert "Verified" in r.text
    r = client.post("/signin", json={
        "email": "dana@example.test", "password": "hunter2-hunter2"})
    assert r.status_code == 200, r.text
    assert r.json()["account_token"]


def test_a_stale_or_garbage_link_refuses(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    token = _link_token_from(sent[0])
    assert client.get(f"/verify-email/click?token={token}").status_code == 200
    assert client.get("/verify-email/click?token=not-a-token").status_code == 403


def test_without_a_mail_transport_signup_activates_directly(client, monkeypatch):
    """A deployment that cannot send mail cannot prove an inbox — and on the
    local single-user install there is nothing to prove. Signup returns the
    session; no dead-end screen waiting for an email that cannot come."""
    monkeypatch.setattr(mailer, "configured_transport", lambda: "console")
    r = _signup(client)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["verification"] == "local"
    assert body["account_token"]
    assert client.post("/signin", json={
        "email": "dana@example.test",
        "password": "hunter2-hunter2"}).status_code == 200


def test_console_mail_survives_a_cp1252_stdout(capsys, monkeypatch):
    """The frozen Windows backend's stdout is cp1252. The first shipped
    banner used box-drawing characters that encoding cannot represent, so
    printing the verification code raised — and every signup answered 500 on
    the one platform the console transport serves most. The banner must be
    encodable there, forever."""
    monkeypatch.delenv("QRME_SMTP_HOST", raising=False)
    assert mailer.deliver("dana@example.test", "Your code",
                          "Your verification code is: 123456") == "console"
    out = capsys.readouterr().out
    assert "123456" in out
    out.encode("cp1252")   # raises if the banner regresses


def test_a_short_password_is_refused_before_any_email_is_sent(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    assert _signup(client, password="short").status_code == 422
    assert sent == []
