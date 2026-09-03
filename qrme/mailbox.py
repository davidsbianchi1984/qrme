"""The moderated mailbox — every synthetic profile's own correspondence.

Lifted from JIM-mini's coach mailbox (`jim/mailbox.py`) with the role turned
into the thing it was written to become: **the profession**. A profile
answers its email as itself — Dr. Osei writes as a physician, the plumber
as a plumber — through the same persona prompt every other surface speaks
from, so the voice in the mail is the voice in the room.

## Who works the inbox

The profile does. That is the owner's line for this product, and it is a
different line from JIM's: a synthetic profile here is a professional that
*operates*, and an inbox it could not read or answer on its own would be a
desk with nobody at it.

* **It reads.** An inbound message lands in a thread (:func:`receive`) —
  today from the operator handing it in, tomorrow from the profile's own
  inbox connection: a Gmail, Outlook or Mail connector attached on the
  Plug-ins screen is the inbox the profile works, and :func:`posture` names
  which one is attached and whether it is signed in. The wire that carries a
  new message *in* is real in two shapes (3.0.4): a per-profile **inbound
  webhook** any mail provider can POST to (:func:`land`, token-gated), and
  an **IMAP poll** over the attached connector's sealed credential
  (:func:`poll`), on a press or on the deployment's own poller
  (``QRME_MAIL_POLL_MINUTES``). :func:`posture` says which of the two is
  wired for this profile; ``inbound_ready`` is true only when one is.
* **It drafts and replies.** On arrival, a profile in ``auto`` moderation
  mode answers on its own: it composes the reply, screens it through the
  same :mod:`qrme.moderation` every chat turn passes, and carries it out —
  sent over the deployment's mail when one is wired, *staged* (composed and
  held, never dropped, never claimed sent) when none is. A profile in
  ``manual`` mode does everything but the last step: the reply is held for
  its owner. That is the one switch, and it is the switch the product
  already has — the same ``moderation_mode`` that decides whether a chat
  reply waits for the owner decides whether a mail reply does.
* **It is moderated.** A reply the screen flags is held whatever the mode,
  with the reason on it. Nothing flagged leaves on its own.

## Who reviews it

The operator, from their own corner. :func:`desk` gathers every mailbox an
account is answerable for — the profiles it holds under its own name, and
the profiles seated in its companies — with what is held in each, and the
account token is what opens it. A person with twelve profiles reads twelve
inboxes from one desk and approves, edits or discards from there; a profile
in ``auto`` mode has already answered, and the desk shows what it said.
"""

from __future__ import annotations

import email
import email.policy
import hashlib
import imaplib
import json
import logging
import os
import secrets
import threading
import time

from . import db, llm, mailer, moderation

logger = logging.getLogger("qrme.mailbox")

#: Connector apps that are an inbox — the ones a profile can work its mail
#: through. Keyed on the catalog's own app names (qrme/catalog.py).
INBOX_APPS = ("mail", "gmail", "outlook")

#: What the profile's mail skill does. Named so a screen can say it rather
#: than guess, and so the posture is a list rather than a paragraph.
SKILLS = ("read", "draft", "reply", "moderate")

#: Where each inbox connector's mail is read from. The connector's own
#: credential (sealed in the vault at authorize time — an app password, and
#: the address it belongs to) is what logs in; nothing else is asked for.
IMAP_HOSTS = {"gmail": "imap.gmail.com", "outlook": "outlook.office365.com",
              "mail": "imap.mail.me.com"}

#: How many unread messages one poll takes in. A mailbox with a thousand
#: unread is a mailbox somebody should look at, not one the profile should
#: answer a thousand times in a minute.
POLL_CAP = 20


def poll_minutes() -> int:
    """The deployment's own poller interval, or 0 for off."""
    try:
        return max(0, int(os.environ.get("QRME_MAIL_POLL_MINUTES") or 0))
    except ValueError:
        return 0


class MailboxError(ValueError):
    pass


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #

def connections(profile_id: str) -> list[dict]:
    """The inbox connectors this profile has attached, signed in or not."""
    rows = db.connect().execute(
        "SELECT id, provider, app, label, authorized_at FROM app_connectors"
        " WHERE profile_id=? AND status='active' ORDER BY rowid",
        (profile_id,)).fetchall()
    return [{"id": r["id"], "provider": r["provider"], "app": r["app"],
             "label": r["label"], "authorized": bool(r["authorized_at"])}
            for r in rows if r["app"] in INBOX_APPS]


def posture(profile_id: str) -> dict:
    """What this profile's mailbox is: who works it, which way mail can
    carry, and that a flagged reply never leaves on its own."""
    profile = db.connect().execute(
        "SELECT moderation_mode FROM profiles WHERE id=?",
        (profile_id,)).fetchone()
    mode = profile["moderation_mode"] if profile else "manual"
    transport = mailer.configured_transport()
    attached = connections(profile_id)
    webhook_set = _inbound_hash(profile_id) is not None
    pollable = any(c["authorized"] and c["app"] in IMAP_HOSTS for c in attached)
    return {
        "built": True,
        "self_operated": mode == "auto",
        "held_for_owner": mode != "auto",
        "moderation_mode": mode,
        "skills": list(SKILLS),
        "connections": attached,
        "inbox_attached": any(c["authorized"] for c in attached),
        "outbound_transport": transport,
        "outbound_ready": transport == "smtp",
        # The inbound wire: a token-gated webhook a provider POSTs to, or
        # an IMAP poll over the attached connector's sealed credential.
        "inbound_ready": webhook_set or pollable,
        "inbound": {
            "webhook_url": inbound_url(profile_id),
            "webhook_set": webhook_set,
            "pollable": pollable,
            "poll_minutes": poll_minutes(),
        },
        "moderated": True,
        "note": ("the profile reads its own mail, drafts the reply in its "
                 "profession, screens it, and — in auto mode — answers on "
                 "its own; in manual mode the reply is held for its owner. "
                 "A flagged reply is held whatever the mode. Outbound sends "
                 "over SMTP when configured and is otherwise staged. Inbound "
                 "arrives on its own through the profile's inbound address "
                 "(a webhook any mail provider can post to, opened by a "
                 "token minted here) or by polling the attached inbox "
                 "connector over IMAP — on a press, or on the deployment's "
                 "poller when QRME_MAIL_POLL_MINUTES is set."),
    }


# --------------------------------------------------------------------------- #
# reads
# --------------------------------------------------------------------------- #

def _thread(profile_id: str, thread_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM mail_threads WHERE id=? AND profile_id=?",
        (thread_id, profile_id)).fetchone()
    if row is None:
        raise MailboxError("no such mail thread")
    return dict(row)


def _message(profile_id: str, message_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM mail_messages WHERE id=? AND profile_id=?",
        (message_id, profile_id)).fetchone()
    if row is None:
        raise MailboxError("no such mail message")
    return dict(row)


def _messages_of(thread_id: str) -> list[dict]:
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM mail_messages WHERE thread_id=? ORDER BY created_at",
        (thread_id,)).fetchall()]


def _public(m: dict) -> dict:
    return {"id": m["id"], "direction": m["direction"], "state": m["state"],
            "from_addr": m["from_addr"], "to_addr": m["to_addr"],
            "subject": m["subject"], "body": m["body"], "note": m["note"],
            "created_at": m["created_at"]}


def inbox(profile_id: str, limit: int = 50) -> list[dict]:
    """Every thread on this profile, newest activity first, each with its
    messages. Held drafts sit in the thread they belong to."""
    threads = db.connect().execute(
        "SELECT * FROM mail_threads WHERE profile_id=? ORDER BY updated_at"
        " DESC LIMIT ?", (profile_id, int(limit))).fetchall()
    out = []
    for t in threads:
        msgs = _messages_of(t["id"])
        out.append({
            "id": t["id"], "correspondent": t["correspondent"],
            "subject": t["subject"], "status": t["status"],
            "updated_at": t["updated_at"],
            "held_drafts": sum(1 for m in msgs if m["state"] == "draft"),
            "messages": [_public(m) for m in msgs],
        })
    return out


def held_by(account_id: str) -> list[dict]:
    """The profiles an account is answerable for: its own, and the ones
    seated in its companies. Each row says which."""
    from . import company as companies
    conn = db.connect()
    seen: dict[str, dict] = {}
    for r in conn.execute(
            "SELECT id, display_name FROM profiles WHERE owner_id=?"
            " ORDER BY created_at, rowid", (account_id,)).fetchall():
        seen[r["id"]] = {"profile_id": r["id"],
                         "display_name": r["display_name"], "via": "own"}
    for co in companies.list_for(account_id):
        for seat in companies.seats(co["id"]):
            pid = seat.get("profile_id")
            if not pid or pid in seen:
                continue
            row = conn.execute(
                "SELECT display_name FROM profiles WHERE id=?",
                (pid,)).fetchone()
            if row is None:
                continue
            seen[pid] = {"profile_id": pid, "display_name": row["display_name"],
                         "via": "company:" + co["name"]}
    return list(seen.values())


def desk(account_id: str) -> dict:
    """The operator's review desk: every mailbox this account is answerable
    for, with what each holds."""
    profiles = []
    held = 0
    for p in held_by(account_id):
        threads = inbox(p["profile_id"])
        mine = sum(t["held_drafts"] for t in threads)
        held += mine
        profiles.append({**p, "held": mine, "threads": threads,
                         "posture": posture(p["profile_id"])})
    return {"account_id": account_id, "profiles": profiles, "held": held,
            "outbound_transport": mailer.configured_transport()}


def owner_of_draft(draft_id: str) -> str | None:
    """Which profile a message belongs to — the desk's way of checking that
    a draft it is asked to moderate is one of its own."""
    row = db.connect().execute(
        "SELECT profile_id FROM mail_messages WHERE id=?",
        (draft_id,)).fetchone()
    return row["profile_id"] if row else None


# --------------------------------------------------------------------------- #
# the doors
# --------------------------------------------------------------------------- #

def receive(profile_id: str, *, from_addr: str, subject: str, body: str,
            answer: bool = True, cloud=None) -> dict:
    """Take an inbound email into a thread, and let the profile work it.

    A profile in ``auto`` mode answers on its own here — drafts, screens,
    carries out. In ``manual`` mode the reply is drafted and held for the
    owner. ``answer=False`` only lands the message (an import that should
    not trigger twelve replies at once).
    """
    from_addr = (from_addr or "").strip()
    body = (body or "").strip()
    if not from_addr:
        raise MailboxError("an inbound email needs a sender address")
    if not body:
        raise MailboxError("an inbound email needs a body")
    subject = (subject or "").strip() or "(no subject)"
    now = db.utcnow()
    conn = db.connect()
    existing = conn.execute(
        "SELECT id FROM mail_threads WHERE profile_id=? AND correspondent=?"
        " AND status='open' ORDER BY updated_at DESC LIMIT 1",
        (profile_id, from_addr)).fetchone()
    if existing:
        tid = existing["id"]
        conn.execute("UPDATE mail_threads SET updated_at=? WHERE id=?",
                     (now, tid))
    else:
        tid = db.new_id("mth")
        conn.execute(
            "INSERT INTO mail_threads (id, profile_id, correspondent, subject,"
            " status, created_at, updated_at) VALUES (?,?,?,?, 'open', ?, ?)",
            (tid, profile_id, from_addr, subject, now, now))
    mid = db.new_id("mim")
    conn.execute(
        "INSERT INTO mail_messages (id, thread_id, profile_id, direction,"
        " state, from_addr, to_addr, subject, body, note, created_at,"
        " updated_at) VALUES (?,?,?, 'inbound', 'received', ?, '', ?, ?, '',"
        " ?, ?)",
        (mid, tid, profile_id, from_addr, subject, body, now, now))
    conn.commit()
    logger.info("profile %s received mail from %s", profile_id, from_addr)
    out = {"thread_id": tid, "message": _public(_message(profile_id, mid)),
           "reply": None, "answered_on_its_own": False}
    if answer:
        worked = _work(profile_id, mid, cloud=cloud)
        out["reply"] = worked["message"]
        out["answered_on_its_own"] = worked["status"] in ("sent", "staged")
    return out


def _work(profile_id: str, message_id: str, cloud=None) -> dict:
    """The profile works one inbound message: draft, screen, and — in auto
    mode — carry out. The one place the mode and the screen decide."""
    drafted = draft(profile_id, message_id, cloud=cloud)
    d = drafted["draft"]
    verdict = moderation.review(d["body"], None, {}, maturity=_maturity(profile_id))
    if not verdict.approved:
        _message_set(d["id"], note=verdict.reason or "held by moderation")
        return {"status": "held", "message": _public(_message(profile_id, d["id"]))}
    if _mode(profile_id) != "auto":
        _message_set(d["id"], note="owner approval required")
        return {"status": "held", "message": _public(_message(profile_id, d["id"]))}
    thread = _thread(profile_id, d_thread(profile_id, d["id"]))
    return _send(profile_id, thread, _message(profile_id, d["id"]))


def d_thread(profile_id: str, message_id: str) -> str:
    return _message(profile_id, message_id)["thread_id"]


def draft(profile_id: str, message_id: str, cloud=None) -> dict:
    """The profile composes a reply to an inbound message and holds it as a
    draft. Drafting never sends; :func:`_work` and :func:`moderate` are the
    two paths out, and both go through the screen."""
    incoming = _message(profile_id, message_id)
    if incoming["direction"] != "inbound":
        raise MailboxError("only an inbound message can be answered")
    thread = _thread(profile_id, incoming["thread_id"])
    reply_body = _compose(profile_id, thread, incoming["body"], cloud=cloud)
    subject = incoming["subject"]
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"
    mid = _hold(profile_id, thread, to_addr=thread["correspondent"],
                subject=subject, body=reply_body)
    return {"thread_id": thread["id"], "draft": _public(_message(profile_id, mid))}


def compose(profile_id: str, *, to: str, subject: str, objective: str,
            cloud=None) -> dict:
    """An outbound message the owner asks the profile to originate.
    ``objective`` is what it should accomplish; the profile writes it and it
    is held for approval — the owner is standing right there."""
    to = (to or "").strip()
    if not to:
        raise MailboxError("an outbound email needs a recipient address")
    if not (objective or "").strip():
        raise MailboxError("an outbound email needs an objective")
    subject = (subject or "").strip() or "(no subject)"
    now = db.utcnow()
    tid = db.new_id("mth")
    conn = db.connect()
    conn.execute(
        "INSERT INTO mail_threads (id, profile_id, correspondent, subject,"
        " status, created_at, updated_at) VALUES (?,?,?,?, 'open', ?, ?)",
        (tid, profile_id, to, subject, now, now))
    conn.commit()
    thread = _thread(profile_id, tid)
    body = _compose(profile_id, thread, objective, originating=True, cloud=cloud)
    mid = _hold(profile_id, thread, to_addr=to, subject=subject, body=body)
    _message_set(mid, note="owner approval required")
    return {"thread_id": tid, "draft": _public(_message(profile_id, mid))}


def moderate(profile_id: str, draft_id: str, action: str,
             edited: str | None = None) -> dict:
    """A person's decision on a held draft. ``approve`` sends it (SMTP if
    configured, otherwise staged and held); ``edit`` replaces the body and
    keeps it held; ``discard`` throws it away and sends nothing."""
    d = _message(profile_id, draft_id)
    if d["direction"] != "outbound" or d["state"] != "draft":
        raise MailboxError("this message is not a draft awaiting moderation")
    thread = _thread(profile_id, d["thread_id"])
    if action == "edit":
        new_body = (edited or "").strip()
        if not new_body:
            raise MailboxError("an edited reply needs a body")
        _message_set(draft_id, body=new_body)
        return {"status": "held", "message": _public(_message(profile_id, draft_id))}
    if action == "discard":
        _message_set(draft_id, state="discarded")
        return {"status": "discarded",
                "message": _public(_message(profile_id, draft_id))}
    if action == "approve":
        return _send(profile_id, thread, d)
    raise MailboxError("a moderation action is approve, edit, or discard")


def _send(profile_id: str, thread: dict, d: dict) -> dict:
    """Carry an approved reply out. SMTP when wired; staged and held
    otherwise — the receipt names which, and never claims a send that did
    not happen."""
    transport = mailer.configured_transport()
    if transport == "smtp":
        mailer.deliver(d["to_addr"], d["subject"], d["body"])
        _message_set(d["id"], state="sent", note="")
        logger.info("profile %s sent mail to %s", profile_id, thread["correspondent"])
        return {"status": "sent", "transport": "smtp",
                "message": _public(_message(profile_id, d["id"]))}
    _message_set(d["id"], state="staged",
                 note="composed and held: no mail transport is configured")
    return {"status": "staged", "transport": "none",
            "message": _public(_message(profile_id, d["id"]))}


# --------------------------------------------------------------------------- #
# the inbound wire
# --------------------------------------------------------------------------- #

def inbound_url(profile_id: str) -> str:
    """Where a mail provider posts this profile's inbound mail."""
    return f"{mailer.public_url()}/mail/inbound/{profile_id}"


def _inbound_hash(profile_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT mail_inbound_token FROM profiles WHERE id=?",
        (profile_id,)).fetchone()
    return row["mail_inbound_token"] if row and row["mail_inbound_token"] else None


def mint_inbound_token(profile_id: str) -> dict:
    """A fresh token that opens this profile's inbound address, shown once.
    Minting again rotates it — the old one stops opening the door."""
    token = "mib_" + secrets.token_urlsafe(24)
    conn = db.connect()
    conn.execute("UPDATE profiles SET mail_inbound_token=? WHERE id=?",
                 (hashlib.sha256(token.encode()).hexdigest(), profile_id))
    conn.commit()
    return {"profile_id": profile_id, "token": token, "shown_once": True,
            "url": inbound_url(profile_id)}


def inbound_opens(profile_id: str, token: str | None) -> bool:
    held = _inbound_hash(profile_id)
    if not held or not token:
        return False
    return secrets.compare_digest(
        held, hashlib.sha256(token.strip().encode()).hexdigest())


#: The field names the common inbound-parse webhooks post under. One
#: landing that reads them all beats a landing per provider: SendGrid's
#: Inbound Parse, Mailgun's routes, Postmark's inbound and a plain JSON
#: post from anything else all arrive at the same door.
_FROM_KEYS = ("from_addr", "from", "sender", "From")
_SUBJECT_KEYS = ("subject", "Subject")
_BODY_KEYS = ("body", "text", "body-plain", "stripped-text", "TextBody",
              "plain")


def parse_inbound(payload: dict) -> dict:
    """The three fields a landing needs, from whatever shape posted them."""
    def pick(keys):
        for k in keys:
            v = payload.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""
    sender = pick(_FROM_KEYS)
    # "Rosa <rosa@example.com>" → the address is the thread's key.
    if "<" in sender and sender.endswith(">"):
        sender = sender[sender.rindex("<") + 1:-1].strip()
    return {"from_addr": sender, "subject": pick(_SUBJECT_KEYS),
            "body": pick(_BODY_KEYS)}


def land(profile_id: str, payload: dict, cloud=None) -> dict:
    """A provider's post lands as an inbound message, and the profile works
    it exactly as it would one handed in."""
    fields = parse_inbound(payload)
    return receive(profile_id, from_addr=fields["from_addr"],
                   subject=fields["subject"], body=fields["body"],
                   cloud=cloud)


def _credential(cid: str, pdi) -> dict | None:
    """The sealed credential an inbox connector was authorized with — the
    app password and the address — read back from the vault. None when
    there is no vault to read from, or nothing was sealed."""
    if pdi is None:
        return None
    row = db.connect().execute(
        "SELECT secret_ref FROM app_connectors WHERE id=?", (cid,)).fetchone()
    if row is None or not row["secret_ref"]:
        return None
    try:
        raw = pdi.get(row["secret_ref"])
        got = json.loads(raw) if raw else None
    except Exception:  # noqa: BLE001 — an unreached tandem is "no credential"
        return None
    if not got or not got.get("secret") or not got.get("account"):
        return None
    return {"account": got["account"], "secret": got["secret"]}


def _imap_fetch(host: str, account: str, secret: str,
                cap: int = POLL_CAP) -> list[dict]:
    """Unread messages in the inbox, marked read as they are taken."""
    out: list[dict] = []
    box = imaplib.IMAP4_SSL(host, 993, timeout=30)
    try:
        box.login(account, secret)
        box.select("INBOX")
        status, data = box.search(None, "UNSEEN")
        ids = data[0].split() if status == "OK" and data and data[0] else []
        for mid in ids[:cap]:
            status, parts = box.fetch(mid, "(RFC822)")
            if status != "OK" or not parts or not isinstance(parts[0], tuple):
                continue
            msg = email.message_from_bytes(parts[0][1], policy=email.policy.default)
            body = msg.get_body(preferencelist=("plain", "html"))
            text = body.get_content() if body is not None else ""
            sender = email.utils.parseaddr(msg.get("From", ""))[1]
            out.append({"from_addr": sender, "subject": msg.get("Subject", ""),
                        "body": text})
    finally:
        try:
            box.logout()
        except Exception:  # noqa: BLE001
            pass
    return out


def poll(profile_id: str, pdi=None, cloud=None, fetcher=None) -> dict:
    """Read the attached inbox connectors over IMAP and let the profile
    work whatever arrived. Each connector reports what happened to it —
    fetched, answered, held, or why it was skipped — rather than the poll
    failing as a whole because one of three could not be reached."""
    from . import offline
    fetch = fetcher or _imap_fetch
    report: list[dict] = []
    for c in connections(profile_id):
        row = {"id": c["id"], "app": c["app"], "fetched": 0, "answered": 0,
               "held": 0, "skipped": None}
        host = IMAP_HOSTS.get(c["app"])
        cred = _credential(c["id"], pdi) if c["authorized"] else None
        if host is None:
            row["skipped"] = "not an inbox this platform reads over IMAP"
        elif not c["authorized"]:
            row["skipped"] = "not signed in — authorize it on Plug-ins"
        elif cred is None:
            row["skipped"] = "its credential could not be read from the vault"
        else:
            try:
                offline.allow_host(host, "reading mail", on_behalf_of=profile_id)
                messages = fetch(host, cred["account"], cred["secret"])
            except Exception as exc:  # noqa: BLE001 — said, not hidden
                row["skipped"] = f"the inbox could not be read: {type(exc).__name__}"
                logger.warning("profile %s: inbox %s unread: %s", profile_id,
                               c["app"], exc)
                report.append(row)
                continue
            for m in messages:
                if not m.get("from_addr") or not (m.get("body") or "").strip():
                    continue
                got = receive(profile_id, from_addr=m["from_addr"],
                              subject=m.get("subject", ""), body=m["body"],
                              cloud=cloud)
                row["fetched"] += 1
                if got["answered_on_its_own"]:
                    row["answered"] += 1
                elif got["reply"] and got["reply"]["state"] == "draft":
                    row["held"] += 1
        report.append(row)
    return {"profile_id": profile_id, "connectors": report,
            "fetched": sum(r["fetched"] for r in report),
            "answered": sum(r["answered"] for r in report),
            "held": sum(r["held"] for r in report)}


def pollable_profiles() -> list[str]:
    """Every profile with a signed-in inbox connector this platform reads."""
    rows = db.connect().execute(
        "SELECT DISTINCT profile_id FROM app_connectors WHERE status='active'"
        " AND authorized_at IS NOT NULL AND app IN (%s)"
        % ",".join("?" * len(IMAP_HOSTS)), tuple(IMAP_HOSTS)).fetchall()
    return [r["profile_id"] for r in rows]


def poll_all(pdi=None, cloud=None, fetcher=None) -> dict:
    """One round of the deployment's poller: every pollable profile, each
    on its own — one profile's unreachable inbox is not another's."""
    out = {"profiles": 0, "fetched": 0, "answered": 0, "held": 0}
    for pid in pollable_profiles():
        try:
            got = poll(pid, pdi=pdi, cloud=cloud, fetcher=fetcher)
        except Exception as exc:  # noqa: BLE001
            logger.warning("poller: profile %s: %s", pid, exc)
            continue
        out["profiles"] += 1
        for k in ("fetched", "answered", "held"):
            out[k] += got[k]
    return out


def start_poller(app) -> threading.Thread | None:
    """The deployment's own poller, when QRME_MAIL_POLL_MINUTES is set.
    A daemon thread that rounds every pollable profile on the interval;
    off entirely when the variable is blank, which is the default and the
    suite's posture."""
    minutes = poll_minutes()
    if minutes <= 0:
        return None

    def run():
        while True:
            time.sleep(minutes * 60)
            try:
                got = poll_all(pdi=app.state.pdi, cloud=app.state.cloud)
                if got["fetched"]:
                    logger.info("poller: %s", got)
            except Exception as exc:  # noqa: BLE001
                logger.warning("poller round failed: %s", exc)

    thread = threading.Thread(target=run, name="qrme-mail-poller", daemon=True)
    thread.start()
    logger.info("mail poller started: every %s minute(s)", minutes)
    return thread


# --------------------------------------------------------------------------- #
# the voice, and the plumbing under it
# --------------------------------------------------------------------------- #

def _profile(profile_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone()
    if row is None:
        raise MailboxError("profile not found")
    return dict(row)


def _mode(profile_id: str) -> str:
    return _profile(profile_id)["moderation_mode"]


def _maturity(profile_id: str) -> str:
    return _profile(profile_id).get("maturity") or "balanced"


def _system(profile: dict, thread: dict) -> str:
    """The profile's standing instruction for its mail: the persona prompt
    every surface speaks from, then the profession and the form."""
    from . import persona
    base = persona.build_system_prompt(profile, None, None)
    trade = profile.get("industry") or "your own field"
    base += (
        f"\n\nYou are answering your own email correspondence, in your "
        f"professional capacity ({trade}). Be courteous, precise, and "
        "helpful; stay within your role, and write a complete email — a "
        "greeting, the message, and a sign-off — in plain text. The thread "
        f"is with {thread['correspondent']}, subject: {thread['subject']}.")
    return base


def _compose(profile_id: str, thread: dict, prompt: str,
             originating: bool = False, cloud=None) -> str:
    profile = _profile(profile_id)
    lines = []
    for m in _messages_of(thread["id"]):
        if m["state"] == "discarded":
            continue
        who = "Them" if m["direction"] == "inbound" else "You"
        lines.append(f"{who}: {m['body']}")
    transcript = "\n\n".join(lines)
    if originating:
        user_turn = f"Write an email that accomplishes this: {prompt}"
    else:
        user_turn = (f"Reply to the latest email.\n\nThe thread so far:\n"
                     f"{transcript}\n\nThe email to answer:\n{prompt}")
    provider = llm.provider_for_profile(profile_id, cloud=cloud)
    text = provider.generate(_system(profile, thread),
                             [{"role": "user", "content": user_turn}])
    return (text or "").strip()


def _hold(profile_id: str, thread: dict, *, to_addr: str, subject: str,
          body: str) -> str:
    now = db.utcnow()
    mid = db.new_id("mim")
    conn = db.connect()
    conn.execute(
        "INSERT INTO mail_messages (id, thread_id, profile_id, direction,"
        " state, from_addr, to_addr, subject, body, note, created_at,"
        " updated_at) VALUES (?,?,?, 'outbound', 'draft', '', ?, ?, ?, '',"
        " ?, ?)",
        (mid, thread["id"], profile_id, to_addr, subject, body, now, now))
    conn.execute("UPDATE mail_threads SET updated_at=? WHERE id=?",
                 (now, thread["id"]))
    conn.commit()
    return mid


def _message_set(message_id: str, **cols) -> None:
    cols["updated_at"] = db.utcnow()
    sets = ", ".join(f"{k}=?" for k in cols)
    conn = db.connect()
    conn.execute(f"UPDATE mail_messages SET {sets} WHERE id=?",
                 (*cols.values(), message_id))
    conn.commit()
