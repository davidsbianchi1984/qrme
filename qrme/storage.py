"""Where a plan's data lives, and what that honestly means.

There are two postures, and the difference between them is the thing Basic
actually buys.

* **open_cloud** — the free tier. Data sits in the platform's own database, in
  the clear. The operator can read it. A backup contains it. A subpoena reaches
  it. Nothing here is encrypted at rest under a key the user holds, and there
  is no vault involved at any point.
* **vault** — Basic and Pro. Content goes to PDI sealed, under a key the
  customer can hold themselves, with a tamper-evident audit chain over every
  access.

**Free and paid differ in where your data lives, not in what you can do**, and
that is the product decision this module encodes. Twenty dollars buys privacy
rather than features. A free tier crippled into uselessness teaches nobody
anything about the product; a free tier that is honestly *not private* teaches
somebody exactly what they are choosing between.

**So the disclosure has to be structural, and it is.** :func:`disclosure` is
carried on every surface that stores something, `not_private` is a field rather
than a footnote, and :func:`posture_of` is the one place the question is
answered. A privacy claim that lives in a Terms of Service and not in the
response body is a claim nobody reads at the moment it matters.

**Some things are refused rather than quietly exposed.**

This is the part that is not negotiable, and it is where "not private" stops
being a user's own business. :data:`SENSITIVE` names payloads whose exposure
harms somebody who never chose the plan — source material somebody handed over
about a third party, and a rated profile's content. Storing those in the
clear because the account holder picked the free option would be
the platform making that choice on behalf of everybody in the frame.

The list is short on purpose and holds only what *this* repository can refuse.
JIM-mini keeps its own for a photograph of a body and a clinical note, because
a kind named here that nothing here enforces would be a claim with no check
behind it.

The alternative — letting free store anything and warning loudly — sounds more
respectful of the user's autonomy and is not, because the person exposed is
frequently not the person who clicked.

**A downgrade never dumps the vault into the open.** Moving from Basic to Free
leaves everything already sealed exactly where it is, sealed. New content goes
to the open store from that moment. The reverse — a downgrade that quietly
unsealed a year of records — is the worst thing this module could do, and
:func:`downgrade_effect` exists to state it rather than to perform it.

**And an upgrade does not un-expose anything.** Content written in the clear
was in the clear. Sealing it afterwards protects it from here on and changes
nothing about the backups, logs and copies that already exist, and
:func:`upgrade_effect` says so in those words.
"""

from __future__ import annotations

POSTURES: dict[str, dict] = {
    "open_cloud": {
        "private": False,
        "title": "Open cloud",
        "means": "your data sits in the platform's own database, in the clear",
        "who_can_read": ("you", "anyone you share with",
                         "the people who operate this deployment",
                         "anyone with lawful access to it"),
        "encrypted_at_rest": False,
        "audit_chain": False,
        "you_hold_a_key": False,
    },
    "vault": {
        "private": True,
        "title": "Encrypted vault",
        "means": "content is sealed in PDI before it lands, under a key you "
                 "can hold yourself",
        "who_can_read": ("you", "anyone you share with"),
        "encrypted_at_rest": True,
        "audit_chain": True,
        "you_hold_a_key": True,
    },
}

# Plan -> posture. The whole of what Basic buys.
BY_PLAN: dict[str, str] = {
    "visitor": "open_cloud",     # a visitor stores nothing; posture is moot
    "free": "open_cloud",
    "basic": "vault",
    "pro": "vault",
}

# What may never sit in the open store, and why — in the words the refusal
# returns.
#
# The test for this entry is not "would the account holder mind". It is
# **whose exposure is it**: every one below is a payload where the person
# harmed is frequently not the person who chose the plan.
#
# Only what *this* repository can actually refuse. JIM-mini keeps its own list
# for its own payloads — a photograph of a body, a clinical note — because a
# kind named here that nothing here enforces would be a claim with no check
# behind it, which is the exact gap this codebase keeps finding in itself.
# `test_every_sensitive_kind_is_enforced_somewhere` holds the line.
SENSITIVE: dict[str, str] = {
    "third_party_source": "source material about a person who is not you — "
                          "they did not pick this plan",
    "rated_content": "content behind the age gate",
}

# Deliberately *not* here, and worth recording because the first version got it
# wrong: a **signing credential**. It reads like the most sensitive thing in
# the product and is not a storage-at-rest risk at all — WebAuthn keeps the
# private key on the device, and what this repository stores is a public key
# and assertions over challenges it minted. There is nothing for an open store
# to expose.
#
# Gating it also broke signing outright, because the signer is frequently an
# *interactor* with no membership at all: `plan_of` returned "visitor", the
# posture came back open_cloud, and every enrolment was refused. A sensitive
# list assembled by intuition about which words sound alarming is how that
# happens.

FREE_DISCLOSURE = (
    "This account is on the free plan. Your data is stored in the clear — no "
    "vault, no encryption you hold the key to, and the people who run this "
    "deployment can read it. That is what free means here, and it is the only "
    "difference from Basic: the features are the same."
)


class StorageError(ValueError):
    """A payload that cannot be stored under this posture."""


def posture_of(plan: str) -> str:
    """The one place this question is answered."""
    return BY_PLAN.get(plan, "open_cloud")


def is_private(plan: str) -> bool:
    return POSTURES[posture_of(plan)]["private"]


def describe(plan: str) -> dict:
    """What this plan's storage actually is, for a surface to show.

    Returned as a field rather than left to a Terms of Service, because a
    privacy claim nobody reads at the moment it matters is not a claim.
    """
    posture = posture_of(plan)
    spec = POSTURES[posture]
    return {
        "plan": plan,
        "posture": posture,
        "private": spec["private"],
        "not_private": not spec["private"],
        "title": spec["title"],
        "means": spec["means"],
        "who_can_read": list(spec["who_can_read"]),
        "encrypted_at_rest": spec["encrypted_at_rest"],
        "audit_chain": spec["audit_chain"],
        "you_hold_a_key": spec["you_hold_a_key"],
        "disclosure": FREE_DISCLOSURE if not spec["private"] else None,
        "refused_here": sorted(SENSITIVE) if not spec["private"] else [],
    }


def may_store(plan: str, kind: str) -> bool:
    """Whether this payload may be stored under this plan's posture."""
    if is_private(plan):
        return True
    return kind not in SENSITIVE


def require(plan: str, kind: str) -> None:
    """Raise unless this payload may be stored. Text meant for a person."""
    if may_store(plan, kind):
        return
    raise StorageError(
        f"{SENSITIVE[kind]}. The free plan stores everything in the clear, "
        "and this is not ours to expose on somebody else's behalf — the "
        "person in the frame is often not the person who chose the plan. "
        "Basic seals it in the vault for $20 a month, and the vault itself "
        "is free to host."
    )


def upgrade_effect(from_plan: str, to_plan: str) -> dict:
    """What moving up does, and — more importantly — what it does not.

    Sealing content afterwards protects it from here on. It changes nothing
    about the backups, logs and copies that already exist, and a product that
    implied otherwise would be selling absolution rather than encryption.
    """
    was_open = not is_private(from_plan)
    now_private = is_private(to_plan)
    return {
        "from": from_plan,
        "to": to_plan,
        "new_content_sealed": now_private,
        "existing_content_sealed": False,
        "note": (
            "anything written while you were on the free plan was written in "
            "the clear. It can be moved into the vault, and that protects it "
            "from now on — it does not un-expose it. Backups, logs and any "
            "copy taken in the meantime already exist."
            if was_open and now_private else
            "nothing changes about where your existing content lives"),
    }


def downgrade_effect(from_plan: str, to_plan: str) -> dict:
    """What moving down does. It does not unseal anything.

    A downgrade that quietly emptied the vault into the open store would be
    the worst thing this module could do — a billing event silently
    declassifying a year of somebody's records. So it does not happen, and
    this function exists to say so rather than to perform it.
    """
    was_private = is_private(from_plan)
    now_open = not is_private(to_plan)
    return {
        "from": from_plan,
        "to": to_plan,
        "existing_stays_sealed": True,
        "new_content_in_the_clear": now_open,
        "note": (
            "everything already in the vault stays in the vault, sealed and "
            "readable. Only what you write from now on goes to the open "
            "store. A lapsed subscription does not declassify your history."
            if was_private and now_open else
            "nothing changes about where your existing content lives"),
    }


def vocabulary() -> dict:
    """Both postures side by side, for a page somebody reads before choosing."""
    return {
        "postures": POSTURES,
        "by_plan": BY_PLAN,
        "sensitive": SENSITIVE,
        "free_disclosure": FREE_DISCLOSURE,
        "the_difference": "Free and Basic run the same app. The difference is "
                          "where your data lives.",
    }
