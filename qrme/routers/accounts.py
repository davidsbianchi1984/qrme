"""Accounts: email + password, with the address verified before sign-in.

The account is what *owns* — its id is the ``owner_id`` profiles are
created under and the ``account_id`` memberships bill to — while every
profile keeps its own owner capability token exactly as before. See
``qrme/accounts.py`` for the storage and proof rules.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import accounts, auth

router = APIRouter()


class Signup(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class SignIn(BaseModel):
    email: str
    password: str


class VerifyEmail(BaseModel):
    email: str
    code: str


class ResendCode(BaseModel):
    email: str


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
        return accounts.signin(body.email, body.password)
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
