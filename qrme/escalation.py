"""When the profile cannot resolve it, and the last door is shut.

A synthetic profile can hand a matter to somebody real — see
:mod:`qrme.briefing`. Some matters do not wait for a butcher or a broker, and
the honest end of that ladder is emergency services.

    asked     can the profile hand this to a professional
    mattered  what happens when it cannot, and nobody has time

This module is that end. It is deliberately the smallest thing that can be
true, because everything about it is dangerous.

## Cannot-resolve is a record, not a mood

:func:`unresolved` writes down that the profile reached its limit on a named
matter. The exits hang off that record rather than off a sentence in a chat
turn, so what was offered, when, and what happened next are all answerable
afterwards by somebody who was not there.

## The waiver is signed ahead, in calm conditions

Reaching emergency services can cost the person money — an ambulance is
billed in most of the places this product runs. So the waiver says so, and it
is signed **when the capability is armed**, not when it is used. Nobody reads
a liability paragraph during an emergency; asking them to is how a person in
trouble ends up reading instead of pressing.

At the press the waiver is *shown* and acknowledged in one tap. The record of
what they signed is the text itself, hashed, so "they agreed" is a thing a
third party can check rather than a boolean this product set.

## The dialer is real, and the last door is shut

The press is explicit — nothing here fires on the profile's own judgement.
The path is a real one: a deployment that configures a dialer has a genuine
connection to place a call over.

And while :data:`SEAL` is on, **the final hop refuses**. Not a mock that
returns success, not a button wired to nothing: the call is attempted and
stopped at the point it would leave, and what comes back says exactly that
and gives the person the number to dial themselves. During a beta nobody
should be summoning an ambulance through software that has never been
end-to-end tested, and the way to be sure of that is to make it impossible
rather than to intend it.

The rule the refusal follows is the one the beacon alarms round settled: an
alarm that says help was called has to have called it. So this one never says
help was called. It says the opposite, in the reader's language, with the
number beside it.

## What no argument can do

There is no parameter, plan, profile setting or request field that opens the
seal. The only thing that opens it is the deployment's own
``QRME_DIALER_ARMED``, read at the moment of the call rather than cached at
import — a value read once at start-up is a value that cannot be turned off
without a restart, and this is the one switch that should never need one.
"""

from __future__ import annotations

import os

from . import db, i18n, privileges, signatures

_TRUTHY = {"1", "true", "yes", "on"}

#: The waiver, in the words the person signs. Hashed and stored with the
#: signature, because "they agreed" is a claim and this is the evidence.
WAIVER = (
    "If this profile reaches emergency services on my behalf, I understand "
    "that services rendered may be charged to me — an ambulance, a callout, "
    "a hospital transfer — exactly as they would be if I called myself. I am "
    "arming this now, in my own time, so that pressing it later is one press."
)


class NotArmed(RuntimeError):
    """Refused: nobody has signed the waiver on this account."""


class Sealed(RuntimeError):
    """Refused at the last hop: the dialer is sealed for this deployment.

    Its own exception rather than a return value, for the reason
    :class:`qrme.offline.LeftTheHost` gives: a caller that could ignore the
    answer is a caller that will, and this is the answer that must not be
    ignored.
    """


def sealed() -> bool:
    """Is the last door shut?

    Read here, every time, rather than captured at import. A deployment that
    has to restart to shut this is a deployment that will leave it open.
    """
    return os.environ.get("QRME_DIALER_ARMED", "").strip().lower() not in _TRUTHY


def emergency_number() -> str:
    """What to dial instead, in this deployment's country.

    Deliberately a deployment setting with a conservative default rather than
    something inferred from a profile's language: guessing 999 at somebody in
    Ohio is worse than saying nothing, and this string is read by a person who
    needs it to be right the first time.
    """
    return os.environ.get("QRME_EMERGENCY_NUMBER", "your local emergency number")


# --------------------------------------------------------------------------
# Arming: the waiver, signed ahead
# --------------------------------------------------------------------------

def arm(interactor_id: str, signature_id: str) -> dict:
    """Record that this person has signed the waiver, and what they signed.

    ``signature_id`` is a verified signature over :data:`WAIVER` — the same
    ceremony a referral release uses, for the same reason: a checkbox is the
    app saying the user agreed, and a signature is something a third party can
    check.
    """
    pkg = signatures.package(signature_id)
    if pkg is None:
        raise NotArmed("no such signature")
    if not pkg.get("verification", {}).get("valid"):
        raise NotArmed("that signature does not verify")
    # Over *these* words. A signature raised for something else does not arm a
    # dialer — the same binding argument `referral.release` makes, and for a
    # louder reason.
    if pkg["document_sha256"] != signatures.sha256_hex(WAIVER):
        raise NotArmed(
            "that signature is over different words — sign the waiver as it "
            "reads now")
    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO dial_waivers"
        " (interactor_id, signature_id, waiver, waiver_sha256, signed_at)"
        " VALUES (?,?,?,?,?)",
        (interactor_id, signature_id, WAIVER,
         signatures.sha256_hex(WAIVER), db.utcnow()))
    conn.commit()
    return armed(interactor_id)


def armed(interactor_id: str) -> dict:
    """Whether the press would be answered, and the words that were signed.

    Returns the waiver text either way. A person who has not armed it should
    be able to read what arming would mean *before* deciding, and a person who
    has should be able to re-read what they agreed to.
    """
    row = db.connect().execute(
        "SELECT * FROM dial_waivers WHERE interactor_id=?",
        (interactor_id,)).fetchone()
    return {"armed": row is not None,
            "signed_at": row["signed_at"] if row else None,
            "waiver": WAIVER,
            # What the deployment would do if pressed — said here rather than
            # discovered at the press.
            "sealed": sealed(),
            "call_yourself": emergency_number()}


# --------------------------------------------------------------------------
# Cannot resolve
# --------------------------------------------------------------------------

def unresolved(profile_id: str, interactor_id: str, matter: str) -> dict:
    """The profile has reached its limit on this matter. Write it down.

    The exits hang off this record rather than off a sentence in a chat turn,
    so what was offered and what happened next are answerable afterwards by
    somebody who was not in the room.
    """
    if not matter.strip():
        raise ValueError("say what could not be resolved, in one line")
    eid = db.new_id("esc")
    conn = db.connect()
    conn.execute(
        "INSERT INTO escalations (id, profile_id, interactor_id, matter,"
        " dialed_at, placed, created_at) VALUES (?,?,?,?,NULL,0,?)",
        (eid, profile_id, interactor_id, matter.strip(), db.utcnow()))
    conn.commit()
    return get(eid)


def get(escalation_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM escalations WHERE id=?", (escalation_id,)).fetchone()
    if row is None:
        raise ValueError("no such escalation")
    return {"id": row["id"], "profile_id": row["profile_id"],
            "interactor_id": row["interactor_id"], "matter": row["matter"],
            "dialed_at": row["dialed_at"],
            # Never inferred from "we tried". The only thing that sets this is
            # a call that actually connected.
            "placed": bool(row["placed"]),
            "raised_at": row["created_at"]}


def for_interactor(interactor_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM escalations WHERE interactor_id=?"
        " ORDER BY created_at DESC, rowid DESC", (interactor_id,)).fetchall()
    return [get(r["id"]) for r in rows]


# --------------------------------------------------------------------------
# The press
# --------------------------------------------------------------------------

def _place(number: str) -> None:
    """Where the call would leave, and where it is stopped.

    The seal is *here*, at the last hop, rather than in the route above — the
    argument ``scrape.fetch`` makes for its offline check and ``visits`` makes
    for its stand-down. A second caller added tomorrow inherits the refusal
    instead of remembering it, and there is no path to a telephony provider
    that does not pass through this function.
    """
    if sealed():
        raise Sealed(i18n.fill(i18n.DIALER_SEALED, number=number))
    # A deployment that unseals this configures a real carrier here. Until one
    # is configured there is nothing to place a call over, and saying so is
    # better than a success this product cannot back.
    raise Sealed(i18n.fill(i18n.DIALER_NO_CARRIER, number=number))


def dial(escalation_id: str, interactor_id: str) -> dict:
    """The explicit press.

    Refuses without an armed waiver, then attempts the call and is stopped at
    the last hop. Every answer this can give says plainly whether a call was
    placed, and while the seal is on the answer is always *no* — with the
    number to dial beside it.
    """
    row = get(escalation_id)
    if row["interactor_id"] != interactor_id:
        raise NotArmed("that escalation belongs to somebody else")
    # Two people have to have agreed: the profile's owner, who put this power
    # on the roster, and the person pressing, who signed the waiver. Neither
    # yes stands in for the other.
    privileges.require(row["profile_id"], "reach_emergency_services")
    if not armed(interactor_id)["armed"]:
        raise NotArmed(
            "sign the emergency-services waiver before this can be pressed — "
            "it says that services rendered may be charged to you")
    conn = db.connect()
    conn.execute("UPDATE escalations SET dialed_at=? WHERE id=?",
                 (db.utcnow(), escalation_id))
    conn.commit()
    # Attempted, and stopped. `placed` stays 0 because nothing connected, and
    # the exception carries the sentence the person reads.
    _place(emergency_number())
    raise AssertionError("unreachable: _place never returns")   # pragma: no cover
