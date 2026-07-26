"""Medical referral: find a real clinician, and release the session to them.

``POST /handoffs`` already packages an AI specialist session for a real
provider, seals it in PDI, and hands over a revocable token. It gates that
release on ``body.consent`` — **a boolean the client sets.**

For a mental-health or medical session that is not enough, and the repo
already says so. ``qrme/webauthn.py`` opens by describing itself as *"the
layer that turns 'the app says the user agreed' into something a third party
can check"*, and the entire signing stack — enrolment, proofing levels,
device-bound credentials, envelope challenges, verified evidence packages —
has been sitting one import away from the one endpoint that ships somebody's
health conversation outside the product. A checkbox was authorising it.

So a referral is a handoff with three differences.

**The signature is over the package, not over a promise.** The envelope's
challenge *is* the hash of the exact bytes being released
(``signatures.request`` takes the document and hashes it), and :func:`release`
**re-hashes the stored package at release time** — deliberately not comparing
against the ``document_sha256`` column beside it, which was written in the same
breath and would agree with itself no matter what happened to the row after.
The user does not sign "I agree to share my data"; they sign *this* summary, to
*this* clinician. Change either and the release stops — not as a policy, as
arithmetic.

**It is bound to this referral.** The envelope carries
``binding_kind="referral"`` and ``binding_ref``, so a signature collected for
one purpose cannot be replayed to authorise another. Without that, any valid
assertion from the same account would do.

**The token is one-time.** A handoff token stays live until revoked, which is
right for an ongoing provider relationship and wrong here: this is one
clinician receiving one summary once. Redemption burns it, and a second
attempt is told plainly that it already happened — a replayed link is
something the user should be able to see, not something that silently works.

Matching is deliberately unclever. Expertise is a filter, geography ranks
within it, and a provider is never *invented* to fill a gap: an empty result
is an empty result, because the failure mode of a confident wrong referral is
somebody phoning a clinic that cannot help them.
"""

from __future__ import annotations

import json
import secrets

from . import db, signatures

# Releasing a health conversation is not a "basic" act. `high` additionally
# demands document proofing and a device-bound credential — the platform
# authenticator (Face ID / Touch ID / Optic ID) rather than a syncable
# passkey, so the signature attests to a person at a device and not to
# whoever holds a credential that roams.
TIER = "high"

MEANING = ("I am releasing this summary of my sessions to this clinician, "
           "and I understand they will be able to read it.")


class ReferralError(ValueError):
    """A referral that must not proceed. Carries text meant for a person."""


# --------------------------------------------------------------------------- #
# matching
# --------------------------------------------------------------------------- #

def match(area: str, location: str | None = None,
          limit: int = 5) -> list[dict]:
    """Providers who can help, nearest first.

    Expertise filters and geography ranks — never the other way round. A
    cardiologist two streets away is not a substitute for a psychiatrist, and
    sorting by distance first is how that swap happens quietly.
    """
    rows = db.connect().execute(
        "SELECT * FROM providers WHERE area=? ORDER BY name", (area,)
    ).fetchall()
    out = []
    want = (location or "").strip().lower()
    for r in rows:
        have = (r["location"] or "").strip().lower()
        if want and have:
            local = have == want
        else:
            local = False
        out.append({
            "id": r["id"], "name": r["name"], "area": r["area"],
            "location": r["location"], "contact": r["contact"],
            "business": bool(r["business"]),
            "in_your_area": local,
            # Said plainly rather than scored: a number here would imply a
            # precision the data does not have.
            "match": "area and location" if local else "area of expertise",
        })
    out.sort(key=lambda p: (not p["in_your_area"], p["name"]))
    return out[:limit]


# --------------------------------------------------------------------------- #
# preparing — build the package and mint the envelope to sign
# --------------------------------------------------------------------------- #

def _package(interactor: dict, profile: dict, provider, limit: int = 6) -> dict:
    """What the clinician will receive. Assembled once and hashed, so the
    thing signed and the thing sent cannot diverge."""
    conn = db.connect()
    recent = conn.execute(
        "SELECT role, content FROM messages WHERE profile_id=?"
        " AND interactor_id=? AND status='approved'"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile["id"], interactor["id"], limit)).fetchall()
    return {
        "user": interactor["display_name"],
        "clinician": provider["name"],
        "area": provider["area"],
        # Named as synthetic in the package itself. A clinician reading a
        # transcript must never have to work out whether the other voice was
        # a person — the AI mark is on the portrait, and this is the same
        # disclosure carried into a document that travels without it.
        "specialist": {
            "name": profile["display_name"],
            "synthetic": True,
            "note": "an AI profile, not a clinician; nothing here is a "
                    "diagnosis",
        },
        "recent_exchange": [{"role": r["role"], "content": r["content"]}
                            for r in reversed(recent)],
    }


def _document(package: dict) -> str:
    """The exact bytes signed and later released. Canonical so that the same
    package always hashes the same way."""
    return signatures.canonical(package).decode()


def display_text(package: dict) -> str:
    """What the signer is shown. Stored verbatim and hashed into the payload,
    because WebAuthn cannot attest to what was on screen."""
    n = len(package["recent_exchange"])
    return (
        f"Release {n} message{'s' if n != 1 else ''} from your sessions with "
        f"{package['specialist']['name']} (an AI profile) to "
        f"{package['clinician']} — {package['area']}.\n\n"
        "They will be able to read this summary once. "
        "Nothing else from your account is included."
    )


def prepare(interactor: dict, profile: dict, provider_id: str,
            account_id: str, rp_id: str) -> dict:
    """Build the package and mint the signature envelope that authorises it.

    Nothing is released here and no token exists yet — this only produces the
    challenge the user's authenticator will sign.
    """
    provider = db.connect().execute(
        "SELECT * FROM providers WHERE id=?", (provider_id,)).fetchone()
    if provider is None:
        raise ReferralError("no such clinician")

    package = _package(interactor, profile, provider)
    if not package["recent_exchange"]:
        raise ReferralError(
            "there is nothing to refer yet — this releases your sessions "
            "with the specialist, and there are none")

    referral_id = db.new_id("ref")
    doc = _document(package)
    shown = display_text(package)
    try:
        envelope = signatures.request(
            account_id=account_id, document=doc, meaning=MEANING, tier=TIER,
            display_text=shown, binding_kind="referral",
            binding_ref=referral_id, rp_id=rp_id)
    except signatures.SignatureError as exc:
        # Surfaced rather than swallowed: "you have no credential at this
        # tier" is something the user can act on, and silently dropping to a
        # weaker tier would be the checkbox again wearing a signature's name.
        raise ReferralError(str(exc)) from exc

    conn = db.connect()
    conn.execute(
        "INSERT INTO referrals (id, interactor_id, profile_id, provider_id,"
        " package, document_sha256, envelope_id, signature_id, token,"
        " redeemed_at, created_at) VALUES (?,?,?,?,?,?,?,NULL,NULL,NULL,?)",
        (referral_id, interactor["id"], profile["id"], provider_id,
         json.dumps(package), signatures.sha256_hex(doc),
         envelope["envelope_id"], db.utcnow()))
    conn.commit()
    return {"referral_id": referral_id, "clinician": provider["name"],
            "area": provider["area"], "package": package,
            "display_text": shown, "sign": envelope}


# --------------------------------------------------------------------------- #
# releasing — only against a verified assertion over this package
# --------------------------------------------------------------------------- #

def get(referral_id: str) -> dict | None:
    row = db.connect().execute("SELECT * FROM referrals WHERE id=?",
                               (referral_id,)).fetchone()
    return dict(row) if row else None


def release(referral_id: str, signature_id: str) -> dict:
    """Mint the one-time token, if the signature really authorises this.

    Four things are checked, and each of them has failed somewhere in the
    wild: that the signature verifies at all, that it belongs to this
    referral, that it covers *these* bytes, and that we have not already
    released.
    """
    row = get(referral_id)
    if row is None:
        raise ReferralError("no such referral")
    if row["token"]:
        raise ReferralError("this referral has already been released")

    pkg = signatures.package(signature_id)
    if pkg is None:
        raise ReferralError("no such signature")
    if not pkg.get("verification", {}).get("valid"):
        raise ReferralError("that signature does not verify")
    if pkg["envelope_id"] != row["envelope_id"]:
        raise ReferralError(
            "that signature authorises something else — a referral is "
            "released only by the signature raised for it")
    # Re-hash the package **as it stands now**, rather than trusting the hash
    # recorded beside it. Comparing the stored hash to the signature would be
    # comparing two things written at the same moment: consistent by
    # construction and evidence of nothing. Anything that edited the row after
    # signing would have sailed through.
    current = signatures.sha256_hex(_document(json.loads(row["package"])))
    if pkg["document_sha256"] != current:
        raise ReferralError(
            "the summary changed after it was signed; sign the new one")

    token = f"ref_{secrets.token_urlsafe(24)}"
    conn = db.connect()
    conn.execute(
        "UPDATE referrals SET signature_id=?, token=? WHERE id=?",
        (signature_id, token, referral_id))
    conn.commit()
    return {"id": referral_id, "token": token, "one_time": True,
            "signature_id": signature_id,
            "signed_by": pkg["signer"], "meaning": pkg["meaning"]}


def redeem(referral_id: str, token: str, pdi=None) -> dict:
    """The clinician opens it. Once.

    A second attempt is refused *and named* rather than 404'd: if a link is
    being replayed, the person it belongs to should be able to find out that
    it was.
    """
    row = get(referral_id)
    if row is None or not row["token"]:
        raise ReferralError("no such referral")
    if not secrets.compare_digest(token, row["token"]):
        raise ReferralError("that link is not valid")
    if row["redeemed_at"]:
        raise ReferralError(
            f"this referral was already opened at {row['redeemed_at']} and "
            "a referral link works once")

    conn = db.connect()
    conn.execute("UPDATE referrals SET redeemed_at=? WHERE id=?",
                 (db.utcnow(), referral_id))
    conn.commit()
    return {"id": referral_id, "package": json.loads(row["package"]),
            "signature_id": row["signature_id"],
            "note": "released by the patient under a verified signature; "
                    "this link has now been used and will not open again"}


def history(interactor_id: str) -> list[dict]:
    """What this person has released, to whom, and whether it was opened."""
    return [{"id": r["id"], "provider_id": r["provider_id"],
             "released": bool(r["token"]),
             "opened_at": r["redeemed_at"],
             "signature_id": r["signature_id"],
             "created_at": r["created_at"]}
            for r in db.connect().execute(
                "SELECT * FROM referrals WHERE interactor_id=?"
                " ORDER BY created_at, rowid", (interactor_id,)).fetchall()]
