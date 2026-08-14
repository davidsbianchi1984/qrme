"""Accounts: email + password, with the address verified before sign-in.

The account is what *owns* — its id is the ``owner_id`` profiles are
created under and the ``account_id`` memberships bill to — while every
profile keeps its own owner capability token exactly as before. See
``qrme/accounts.py`` for the storage and proof rules.
"""

from __future__ import annotations

import html

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .. import accounts, auth, mailer

router = APIRouter()


class Signup(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class SignIn(BaseModel):
    email: str
    password: str
    #: The person this device has been talking as, if it has one.
    #:
    #: Somebody talks to three starters as a stranger, then makes an account.
    #: Minting a fresh person at that moment would throw away every
    #: conversation they had just had — the account would be the moment their
    #: history was deleted, which is the worst possible time for it. Handed
    #: over here, that stranger becomes them.
    adopt_interactor_id: str | None = None


class VerifyEmail(BaseModel):
    email: str
    code: str


class ResendCode(BaseModel):
    email: str


class MailSettings(BaseModel):
    """Where this deployment sends mail through (qrme/mailer.py)."""
    host: str
    port: int = 587
    username: str | None = None
    password: str | None = None
    sender: str | None = None
    public_url: str | None = None    # what verification links point at


class MailTest(BaseModel):
    to: str


class ResetRequest(BaseModel):
    email: str


class ResetPassword(BaseModel):
    email: str
    code: str
    new_password: str


@router.post("/signup", status_code=201,
             dependencies=[Depends(auth.require_signup_key)])
def signup(body: Signup) -> dict:
    """Create an account. It cannot sign in until the emailed code proves
    the caller holds the address. The response says how the code travelled
    (``smtp``, or ``console`` — printed to the server terminal when no mail
    is configured), never the code."""
    try:
        return accounts.signup(body.email, body.password, body.display_name)
    except accounts.AccountError as exc:
        raise HTTPException(exc.status, exc.detail)


@router.post("/verify-email")
def verify_email(body: VerifyEmail) -> dict:
    """Trade the emailed code for the account's first session token —
    shown once."""
    try:
        return accounts.verify(body.email, body.code)
    except accounts.AccountError as exc:
        raise HTTPException(exc.status, exc.detail)


@router.get("/verify-email/click", response_class=HTMLResponse)
def verify_email_click(token: str = "") -> HTMLResponse:
    """The emailed link lands here, in a browser. The app finishes on its
    own: it holds the email and password, so it signs in the moment the
    address is proven."""
    page = ("<html><body style='font-family:sans-serif;background:#0d0a20;"
            "color:#e6edf3;display:grid;place-items:center;height:95vh'>"
            "<div style='text-align:center'><h1>{title}</h1><p>{body}</p>"
            "</div></body></html>")
    try:
        result = accounts.verify_link(token)
    except accounts.AccountError as exc:
        return HTMLResponse(page.format(
            title="That link didn't work", body=exc.detail), 403)
    if result["already"]:
        return HTMLResponse(page.format(
            title="Already verified",
            body="This address was verified earlier — just sign in."))
    return HTMLResponse(page.format(
        title="✓ Verified",
        body="Your account is active. Go back to QRME — it will continue "
             "on its own."))


@router.post("/verify-email/resend")
def resend_code(body: ResendCode) -> dict:
    """Send a fresh code, retiring the previous ones. Answers the same
    whether or not the address has an account — this endpoint is not an
    address oracle."""
    try:
        return accounts.resend(body.email)
    except accounts.AccountError as exc:
        raise HTTPException(exc.status, exc.detail)


@router.post("/signin")
def signin(body: SignIn) -> dict:
    """Email + password for a fresh account token. Unknown address and
    wrong password get the same answer; an unverified address cannot sign
    in at all."""
    try:
        return accounts.signin(body.email, body.password,
                               adopt_interactor_id=body.adopt_interactor_id)
    except accounts.AccountError as exc:
        raise HTTPException(exc.status, exc.detail)


@router.post("/password/reset/request")
def request_password_reset(body: ResetRequest) -> dict:
    """Email a reset code. Same answer whether or not the address has an
    account — not an address oracle."""
    try:
        return accounts.request_reset(body.email)
    except accounts.AccountError as exc:
        raise HTTPException(exc.status, exc.detail)


@router.post("/password/reset")
def reset_password(body: ResetPassword) -> dict:
    """Trade the emailed code for a new password. Every existing account
    session dies with the old password; per-profile owner tokens are
    separate capabilities and are untouched."""
    try:
        return accounts.reset_password(body.email, body.code,
                                       body.new_password)
    except accounts.AccountError as exc:
        raise HTTPException(exc.status, exc.detail)


# ---- where this deployment sends mail through ---------------------------

@router.get("/settings/mail")
def get_mail_settings() -> dict:
    """The mail configuration, never its password. Until a host is set, no
    verification email can be sent to anybody — which is why local signup
    does not wait for one."""
    return mailer.describe_settings()


@router.put("/settings/mail",
            dependencies=[Depends(auth.require_signup_key)])
def put_mail_settings(body: MailSettings) -> dict:
    """Point this deployment at a mail server, from the app itself.
    Environment variables still win when set."""
    try:
        return mailer.save_settings(
            host=body.host, port=body.port, username=body.username or "",
            password=body.password or "", sender=body.sender or "",
            public_url=body.public_url or "")
    except ValueError as exc:
        raise HTTPException(422, str(exc))


@router.delete("/settings/mail",
               dependencies=[Depends(auth.require_signup_key)])
def delete_mail_settings() -> dict:
    """Forget the mail server; delivery falls back to the console."""
    return mailer.clear_settings()


@router.post("/settings/mail/test",
             dependencies=[Depends(auth.require_signup_key)])
def test_mail_settings(body: MailTest) -> dict:
    """Send a real message now, and say plainly what the server said. A
    settings screen that saves without ever proving it can deliver is how an
    app ends up insisting it emailed somebody."""
    if mailer.configured_transport() != "smtp":
        raise HTTPException(422, "no mail server is configured — save one first")
    try:
        mailer.deliver(
            body.to, "QRME test message",
            "This is a test from QRME.\n\nIf you are reading it in your "
            "inbox, verification emails will reach your users too.")
    except Exception as exc:  # noqa: BLE001 — smtplib raises many kinds
        raise HTTPException(502, f"the mail server refused it: {exc}")
    return {"sent": True, "to": body.to}


# -- Sign in with Google / Apple ---------------------------------------------
# qrme/oauth.py holds the flow; these routes are its doors. Configuration,
# not code, decides whether a provider is live on this deployment.

from fastapi import Request as _Request

from .. import oauth as oauth_mod


class OAuthStart(BaseModel):
    redirect_uri: str | None = None


@router.get("/auth/oauth/providers")
def oauth_providers() -> dict:
    """Which sign-in doors are live here, and how to open the rest."""
    return oauth_mod.providers()


@router.post("/auth/oauth/{provider}/start")
def oauth_start(provider: str, body: OAuthStart,
                request: _Request) -> dict:
    """Mint a state and the provider's authorize URL. The default return
    address is this API's own callback — right for the desktop app, where
    the backend answers on loopback."""
    redirect = body.redirect_uri or str(
        request.url_for("oauth_callback", provider=provider))
    try:
        return oauth_mod.start(provider, redirect)
    except oauth_mod.OAuthError as exc:
        raise HTTPException(exc.status, exc.message) from None


@router.get("/auth/oauth/{provider}/callback", response_class=HTMLResponse)
def oauth_callback(provider: str, code: str = "", state: str = "",
                   error: str = "") -> HTMLResponse:
    """Where the provider sends the browser back. Finishes the exchange and
    tells the person to return to the app — the app itself claims the
    session at /auth/oauth/claim."""
    if error or not code:
        return HTMLResponse(
            f"<h2>Sign-in was not completed</h2>"
            f"<p>{html.escape(error) or 'no code came back'} — you can close "
            "this window "
            "and try again.</p>",
            status_code=400)
    try:
        done = oauth_mod.callback(provider, code, state)
    except oauth_mod.OAuthError as exc:
        return HTMLResponse(
            f"<h2>Sign-in failed</h2><p>{html.escape(exc.message)}</p>",
                            status_code=exc.status)
    return HTMLResponse(
        f"<h2>Signed in as {html.escape(done['email'])}</h2>"
        "<p>You can close this window and return to the app.</p>")


@router.post("/auth/oauth/{provider}/callback", response_class=HTMLResponse)
async def oauth_callback_post(provider: str,
                              request: _Request) -> HTMLResponse:
    """Apple's half of the door.

    Apple's rule is that requesting any scope forces
    ``response_mode=form_post``, so the browser comes back as a POST with the
    code in a urlencoded body rather than the query string. Parsed from the
    raw body on purpose — the same trick the media upload uses, so no
    python-multipart dependency is added for one form.
    """
    import urllib.parse as _up
    form = _up.parse_qs((await request.body()).decode("utf-8", "replace"))
    return oauth_callback(provider,
                          code=(form.get("code") or [""])[0],
                          state=(form.get("state") or [""])[0],
                          error=(form.get("error") or [""])[0])


@router.get("/auth/oauth/claim")
def oauth_claim(state: str) -> dict:
    """One-time pickup of a completed sign-in. The console polls this after
    opening the browser; the first successful claim spends the state."""
    try:
        return oauth_mod.claim(state)
    except oauth_mod.OAuthError as exc:
        raise HTTPException(exc.status, exc.message) from None
