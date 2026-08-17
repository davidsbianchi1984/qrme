"""Catching a real person up before they walk in.

``referral.prepare`` packages a session for a clinician: the recent exchange,
the specialist named as synthetic, hashed so the thing signed and the thing
sent cannot diverge. That is the right ceremony and it carries the wrong
payload, twice over.

It is **clinical only**, and the question is not. A cook profile handing a
matter to a butcher, a money profile to a broker, a coach to a
physiotherapist — every synthetic profile that can bring somebody real into
it needs the same thing, and needs it to arrive before the provider does.

And it carries **the conversation and nothing else**. A provider stepping
into somebody's matter is not caught up by six messages; they are caught up
by the photographs, the statements, the history, the link the person was sent
last week. A briefing that omits those makes the provider ask for them, which
is the person telling their story twice — once to the profile, once to the
provider — which is the thing the handoff existed to prevent.

    asked     can a session be handed to a professional
    mattered  does the professional arrive already knowing

## What is allowed in, and what decides it

Everything in an attachment comes through :func:`qrme.tasks.scoped_items`,
the one function that reads a revocable grant. Nothing here interprets
``scope`` itself, and that is deliberate: the entire value of a revocable
grant is that revoking it stops *everything*, and a second reading of a scope
is a second place that can read it generously. A profile with no grant
prepares no briefing at all.

So the shape of the promise is exact. **A briefing can carry what the user
granted this profile, and cannot carry anything else** — not because the
assembling code is careful, but because it is never handed anything else.

## The provider is told what they are reading

Two disclosures ride in the document rather than around it, because a
document travels away from the screen that framed it:

* the specialist is **named as synthetic**, in the package, every time; and
* material is stamped with where it came from, so a photograph the user
  uploaded and a note the profile wrote are not the same kind of thing on
  arrival.

## And it is still signed over its own bytes

:func:`document` is canonical, so the same briefing always hashes the same
way, and the signature the user gives is over *these* attachments to *this*
provider. Adding a photograph after signing changes the hash, and the release
stops — as arithmetic rather than as policy.
"""

from __future__ import annotations

from . import db, privileges, signatures, tasks

#: What an attachment says about where it came from. The kinds are the
#: product's own source kinds rather than a new vocabulary, so a briefing
#: cannot describe a thing differently from the screen the user filed it on.
KINDS = ("photo", "conversation", "social_post", "writing", "voice_note",
         "life_event", "knowledge", "linked_account")

#: How much of a long item travels. A briefing is a person's first five
#: minutes with the matter, not an archive — and a provider handed forty
#: pages reads none of them.
EXCERPT = 1200


class NothingToBrief(ValueError):
    """A briefing that must not be assembled. Carries text meant for a
    person."""


def _attachments(profile_id: str, grant_token: str, pdi=None,
                 limit: int = 12) -> list[dict]:
    """The granted material, as things a provider can read.

    Note what is *not* here: a query. The items arrive from
    :func:`qrme.tasks.scoped_items` already filtered by the grant, so there is
    no place in this module where a wider set could be selected by mistake.
    """
    out = []
    for item in tasks.scoped_items(profile_id, grant_token, pdi)[:limit]:
        content = item.get("content") or ""
        out.append({
            "kind": item["kind"],
            "title": item["title"],
            "excerpt": content[:EXCERPT],
            "truncated": len(content) > EXCERPT,
            # Where it came from, carried with it. A photograph the person
            # uploaded and a note the profile wrote are different evidence
            # and must not arrive looking alike.
            "sealed": bool(item["pdi_key"]),
            "filed_at": item["created_at"],
        })
    return out


def assemble(interactor: dict, profile: dict, provider: dict, matter: str,
             grant_token: str, pdi=None, limit: int = 6) -> dict:
    """What the provider will receive, and what the user will sign.

    ``matter`` is the thing being handed over in the user's own terms — the
    briefing's subject line. Without it a provider opens a file of
    attachments and has to infer why they were sent.
    """
    if not matter.strip():
        raise NothingToBrief("say what this is about, in one line")
    # Before anything is read: this is the profile putting somebody's material
    # in front of a third party, and it is the row on the roster that says so.
    privileges.require(profile["id"], "brief_a_professional")
    conn = db.connect()
    recent = conn.execute(
        "SELECT role, content FROM messages WHERE profile_id=?"
        " AND interactor_id=? AND status='approved'"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile["id"], interactor["id"], limit)).fetchall()
    return {
        "user": interactor["display_name"],
        "provider": provider["name"],
        "area": provider["area"],
        "matter": matter.strip(),
        # Named as synthetic in the package itself. A provider reading a
        # transcript must never have to work out whether the other voice was
        # a person — the AI mark is on the portrait, and this is the same
        # disclosure carried into a document that travels without it.
        "specialist": {
            "name": profile["display_name"],
            "synthetic": True,
            "note": "an AI profile, not a professional; nothing here is "
                    "advice from a qualified person",
        },
        "recent_exchange": [{"role": r["role"], "content": r["content"]}
                            for r in reversed(recent)],
        "attachments": _attachments(profile["id"], grant_token, pdi),
    }


def document(package: dict) -> str:
    """The exact bytes signed and later released, canonical so the same
    briefing always hashes the same way."""
    return signatures.canonical(package).decode()


def display_text(package: dict) -> str:
    """What the signer is shown. Stored verbatim and hashed into the payload,
    because WebAuthn cannot attest to what was on screen.

    It counts the attachments out loud. "Your history" is a phrase somebody
    agrees to without knowing what it covers; "4 items, 2 of them photos" is
    a thing they can decline.
    """
    n = len(package["recent_exchange"])
    items = package["attachments"]
    kinds = sorted({a["kind"] for a in items})
    carried = (f"{len(items)} item{'s' if len(items) != 1 else ''} you have "
               f"granted them ({', '.join(kinds)})" if items
               else "no files — only the conversation")
    return (
        f"Bring {package['provider']} into: {package['matter']}.\n\n"
        f"They will receive {n} message{'s' if n != 1 else ''} from your "
        f"sessions with {package['specialist']['name']} (an AI profile), and "
        f"{carried}.\n\n"
        "They can read it once. Nothing else from your account is included, "
        "and revoking the grant stops it."
    )
