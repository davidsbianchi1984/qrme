"""The moderated mailbox's doors — the profile's, and the operator's desk.

Two credentials, two halves. A profile's own mailbox is opened by its owner
token: hand a message in, ask for a draft, originate one, decide on a held
draft. The review desk is opened by the *account* token — the credential a
person has after signing in — and gathers every mailbox the account is
answerable for, its own profiles and its companies' seats, so one person
with twelve profiles reads twelve inboxes from one corner.
"""

from __future__ import annotations

import email
import email.policy
import urllib.parse

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .. import auth, i18n, mailbox
from ..common import profile_or_404, require_owner

router = APIRouter()


class MailReceive(BaseModel):
    from_addr: str
    subject: str = ""
    body: str


class MailCompose(BaseModel):
    to: str
    subject: str = ""
    objective: str


class MailModerate(BaseModel):
    action: str        # approve | edit | discard
    edited: str | None = None


def _refused(exc: Exception) -> HTTPException:
    return HTTPException(422, i18n.raised(exc))


def _form_fields(ctype: str, raw: bytes) -> dict:
    """A provider's form post, read with the standard library.

    Two shapes arrive: urlencoded (Mailgun's routes) and multipart
    (SendGrid's Inbound Parse). Neither needs a dependency this image does
    not carry — a multipart body is MIME, and the mail parser already
    here reads it; the field name rides in each part's disposition.
    """
    if ctype.startswith("multipart/"):
        msg = email.message_from_bytes(
            b"Content-Type: " + ctype.encode() + b"\r\nMIME-Version: 1.0\r\n\r\n"
            + raw, policy=email.policy.default)
        out: dict = {}
        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if not name or part.get_filename():
                continue           # an attachment is not a field
            try:
                out[str(name)] = part.get_content()
            except Exception:  # noqa: BLE001 — a part the parser cannot read
                continue
        return out
    parsed = urllib.parse.parse_qs(raw.decode("utf-8", "replace"),
                                   keep_blank_values=True)
    return {k: v[0] for k, v in parsed.items() if v}


@router.get("/profiles/{profile_id}/mail")
def profile_mail(profile_id: str, request: Request) -> dict:
    """This profile's mailbox: who works it, and every thread on it."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return {"posture": mailbox.posture(profile_id),
            "threads": mailbox.inbox(profile_id)}


@router.post("/profiles/{profile_id}/mail/receive", status_code=201)
def profile_mail_receive(profile_id: str, body: MailReceive,
                         request: Request) -> dict:
    """Hand an inbound message to the profile. It reads it, drafts the reply
    in its profession, screens it, and — in auto mode — answers on its own."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return mailbox.receive(profile_id, from_addr=body.from_addr,
                               subject=body.subject, body=body.body,
                               cloud=request.app.state.cloud)
    except mailbox.MailboxError as exc:
        raise _refused(exc) from None


@router.post("/profiles/{profile_id}/mail/compose", status_code=201)
def profile_mail_compose(profile_id: str, body: MailCompose,
                         request: Request) -> dict:
    """Ask the profile to originate a message. Held for approval."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return mailbox.compose(profile_id, to=body.to, subject=body.subject,
                               objective=body.objective,
                               cloud=request.app.state.cloud)
    except mailbox.MailboxError as exc:
        raise _refused(exc) from None


@router.post("/profiles/{profile_id}/mail/{message_id}/draft",
             status_code=201)
def profile_mail_draft(profile_id: str, message_id: str,
                       request: Request) -> dict:
    """Have the profile draft (or redraft) a reply to an inbound message.
    Held — drafting never sends."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return mailbox.draft(profile_id, message_id,
                             cloud=request.app.state.cloud)
    except mailbox.MailboxError as exc:
        raise _refused(exc) from None


@router.post("/profiles/{profile_id}/mail/{draft_id}/moderate")
def profile_mail_moderate(profile_id: str, draft_id: str, body: MailModerate,
                          request: Request) -> dict:
    """The owner's decision on a held draft: approve, edit, or discard."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return mailbox.moderate(profile_id, draft_id, body.action, body.edited)
    except mailbox.MailboxError as exc:
        raise _refused(exc) from None


@router.post("/profiles/{profile_id}/mail/inbound-token", status_code=201)
def profile_mail_inbound_token(profile_id: str, request: Request) -> dict:
    """Mint (or rotate) the token that opens this profile's inbound mail
    address. Shown once; the database keeps only its hash. Point a mail
    provider's inbound webhook at the URL with the token in
    ``x-mail-inbound-token`` and mail arrives on its own."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return mailbox.mint_inbound_token(profile_id)


@router.post("/profiles/{profile_id}/mail/poll")
def profile_mail_poll(profile_id: str, request: Request) -> dict:
    """Read the attached inbox connectors now, over IMAP, and let the
    profile work what arrived. Each connector says what happened to it."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return mailbox.poll(profile_id, pdi=request.app.state.pdi,
                        cloud=request.app.state.cloud)


@router.post("/mail/inbound/{profile_id}", status_code=201)
async def mail_inbound(profile_id: str, request: Request):
    """A mail provider's inbound post. Opened by the profile's inbound token
    (``x-mail-inbound-token`` header, or ``token`` in the query) and nothing
    else — no client of this product calls it; a provider does. Reads JSON
    or a form, in the field names the common inbound-parse webhooks use."""
    profile_or_404(profile_id)
    token = request.headers.get("x-mail-inbound-token") \
        or request.query_params.get("token")
    if not mailbox.inbound_opens(profile_id, token):
        raise HTTPException(
            403, "that inbound token does not open this profile's mailbox")
    payload: dict = {}
    ctype = request.headers.get("content-type", "")
    raw = await request.body()
    if "json" in ctype:
        try:
            got = await request.json()
            payload = got if isinstance(got, dict) else {}
        except ValueError:
            payload = {}
    else:
        payload = _form_fields(ctype, raw)
    try:
        return JSONResponse(mailbox.land(profile_id, payload,
                                         cloud=request.app.state.cloud),
                            status_code=201)
    except mailbox.MailboxError as exc:
        raise _refused(exc) from None


@router.get("/accounts/{account_id}/mail")
def account_mail_desk(account_id: str, request: Request) -> dict:
    """The operator's review desk: every mailbox this account is answerable
    for — its own profiles and its companies' seats — with what is held."""
    auth.require(request, "account", account_id)
    return mailbox.desk(account_id)


@router.post("/accounts/{account_id}/mail/{draft_id}/moderate")
def account_mail_moderate(account_id: str, draft_id: str, body: MailModerate,
                          request: Request) -> dict:
    """Decide on a held draft from the desk, whichever held profile it
    belongs to. A draft on a profile this account does not hold is refused
    by name rather than found."""
    auth.require(request, "account", account_id)
    pid = mailbox.owner_of_draft(draft_id)
    if pid is None or pid not in {p["profile_id"]
                                  for p in mailbox.held_by(account_id)}:
        raise HTTPException(
            404, "that draft belongs to no profile this account holds")
    try:
        return mailbox.moderate(pid, draft_id, body.action, body.edited)
    except mailbox.MailboxError as exc:
        raise _refused(exc) from None
