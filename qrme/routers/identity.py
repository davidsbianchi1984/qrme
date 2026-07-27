"""Anonymous, several, and exactly one verified.

Mounted on the profile and on the owner. Two of these routes are ordinary and
one is the most sensitive read in the module: `GET /owners/{id}/profiles`
links a person's profiles to each other, which is exactly how you strip the
anonymity off all of them at once. It answers to that owner's own token and to
nothing else, and every anonymity promise here is worth what that check is
worth.

`require_self` is the check, and on this platform an owner token's subject is
the **profile id**, not the `owner_id` string a profile was created with —
holding the token *is* the capability. So the roster is reached through a
profile you can prove you own, and it then lists the account behind it. Asking
for `/owners/{some_owner_id}/profiles` directly would let anybody who learned
an `owner_id` enumerate its profiles, which is the whole attack.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .. import identity
from ..common import profile_or_404, require_owner

router = APIRouter()


class AnonymousIn(BaseModel):
    anonymous: bool


class EmblemIn(BaseModel):
    # A preset field emblem, or your own image, or neither for the plain
    # silhouette. Not both — two pictures for one bubble has no answer.
    emblem: str | None = None
    asset: str | None = None
    # Asked and refused, exactly as the overlay module asks it: nothing here
    # can look at an image and know whose face it is, and an anonymous profile
    # wearing somebody else's is impersonation with deniability on top.
    depicts_someone_else: bool = False


class VerifyIn(BaseModel):
    level: str
    attestor: str | None = None
    method: str | None = None
    ref: str | None = None


@router.get("/identity/vocabulary")
def vocabulary() -> dict:
    """What the three rules are, in the words a screen can show.

    Open: it describes the feature, not anybody's account.
    """
    return {
        "withheld_when_anonymous": list(identity.WITHHELD),
        "never_withheld": list(identity.NOT_WITHHELD),
        "real_person_kinds": list(identity.REAL_PERSON_KINDS),
        "rules": [
            "you may hold as many profiles as you like",
            "any of them may be anonymous, one at a time and independently",
            "at most one of them may be verified, because the badge says you "
            "are a particular real person",
            "the badge moves between your profiles — one at a time, not one "
            "forever",
            "an invented person is unverifiable rather than unverified, and "
            "never uses up your one",
            "anonymity is what we decline to publish, not a promise that "
            "nobody can recognise your writing",
        ],
    }


@router.get("/profiles/{profile_id}/anonymity")
def read_anonymity(profile_id: str, request: Request) -> dict:
    """What this profile's anonymity hides, and what it does not.

    Owner-only, though what it returns is barely a secret — the reason is that
    the *reply names the profile's real display name* when anonymity is off,
    and a route whose answer differs in shape depending on a private flag is a
    route that reports the flag. Owner-only makes it uniformly uninteresting
    to everybody else.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return identity.anonymity(profile_id)


@router.put("/profiles/{profile_id}/anonymity")
def set_anonymity(profile_id: str, body: AnonymousIn,
                  request: Request) -> dict:
    """Turn it on or off. Per profile, never per account.

    An account-wide switch would mean putting your name on the work profile
    puts it on the support-group one, which is the exact coupling that having
    several profiles exists to avoid.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return identity.set_anonymous(profile_id, body.anonymous)


@router.get("/profiles/{profile_id}/badge")
def read_badge(profile_id: str) -> dict:
    """The verification badge as a reader should see it.

    Public, and *not* the same as `GET /profiles/{id}/verification`: on an
    anonymous profile the attestor is withheld, because "checked by Dr Okafor
    of St Mary's" narrows an anonymous author to a city and a workplace. What
    survives is the part worth having — a real person stands behind this and
    somebody checked — which is the difference between a pseudonym and a bot.
    """
    profile_or_404(profile_id)
    return identity.badge(profile_id)


@router.get("/profiles/{profile_id}/verifiable")
def verifiable(profile_id: str, request: Request) -> dict:
    """Whether this profile could take the badge, and if not, why not.

    Owner-only: the answer names *the other profile* that holds the badge,
    which is the linkage the roster is protected for.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return identity.can_verify(profile_id)


@router.post("/profiles/{profile_id}/verification", status_code=201)
def claim(profile_id: str, body: VerifyIn, request: Request) -> dict:
    """Record a verification against this profile, one per person.

    Goes through `identity.verify` rather than `verification.verify` — the
    latter is the storage layer, it does not know about accounts, and a caller
    that reaches past this one gets the second badge the rule exists to
    prevent.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return identity.verify(profile_id, body.level, attestor=body.attestor,
                               method=body.method, ref=body.ref)
    except identity.IdentityError as exc:
        raise HTTPException(409, str(exc)) from None


@router.post("/profiles/{profile_id}/verification/move")
def move(profile_id: str, request: Request) -> dict:
    """Move your badge onto this profile, off whichever one holds it.

    Authorized against the *destination*, which is the profile the caller can
    prove they own. The source is found from the account, so this cannot be
    used to knock a badge off somebody else's profile: if it is not on this
    account there is nothing to move.
    """
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return identity.move(profile["owner_id"], profile_id)
    except identity.IdentityError as exc:
        raise HTTPException(409, str(exc)) from None


@router.get("/profiles/{profile_id}/siblings")
def roster(profile_id: str, request: Request) -> dict:
    """Every profile the same person holds, and which one is verified.

    **The most sensitive read here.** One call that links a person's profiles
    to each other is the whole of what anonymity between them is protecting,
    so it is reached through a profile whose owner token the caller holds, and
    the account is derived from that — never accepted as an id in the path. A
    route keyed on `owner_id` would hand the roster to anybody who learned one,
    and `owner_id` is a string somebody chooses, not a secret.
    """
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    return identity.roster(profile["owner_id"])


@router.get("/places/{surface}/{surface_id}/whose")
def whose(surface: str, surface_id: str) -> dict:
    """Whose live, room, party or stream this is — the top-left corner.

    Public, and it has to be: this is the fact a viewer needs *before* they
    decide anything else about what they are looking at. The burned live mark
    says a real person is behind the camera and deliberately says nothing about
    the mask on their face, and the only reason it can afford that is this —
    the viewer already knows whose account they are on.

    An anonymous profile answers with its silhouette name rather than nothing.
    A viewer still needs to know the stream belongs to one consistent account,
    which is a different fact from knowing which person that is.
    """
    if surface not in identity.WHOSE_SURFACES:
        raise HTTPException(
            422, f"unknown surface {surface!r} — one of "
                 f"{', '.join(identity.WHOSE_SURFACES)}")
    out = identity.whose(surface, surface_id)
    if not out:
        raise HTTPException(404, "no such place")
    return out


@router.get("/identity/emblems")
def emblems() -> dict:
    """The pictures an anonymous profile may wear. Open — it is a catalogue.

    One per industry the platform already models, so the set is not a new
    vocabulary invented for pictures: a field somebody can work in is a field
    they can signal.
    """
    return {"emblems": identity.emblems(),
            "plain": "the silhouette everybody starts with",
            "own_image": "you can upload your own instead — these are a "
                         "shortcut, not the only option",
            "note": "a photograph of your own face is allowed and undoes your "
                    "anonymity to anyone who knows you. Somebody else's "
                    "likeness is refused"}


@router.put("/profiles/{profile_id}/emblem")
def set_emblem(profile_id: str, body: EmblemIn, request: Request) -> dict:
    """What goes in the bubble while this profile is anonymous.

    A preset field emblem, or an image of the owner's own. Owner-only, and
    saveable even when anonymity is off — it simply does not show until it is
    on, the same way a display name waits behind the flag.

    A photograph of the owner's *own* face is allowed. It defeats their
    anonymity and they may have reasons; the response says so plainly rather
    than the platform overruling a choice it cannot evaluate. Somebody else's
    likeness is refused.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return identity.set_picture(profile_id, body.emblem, body.asset,
                                    body.depicts_someone_else)
    except identity.IdentityError as exc:
        raise HTTPException(422, str(exc)) from None
