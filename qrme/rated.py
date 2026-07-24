"""Rated (18+) placement: marketing age-gated profiles at adult venues.

An adult-mode profile — already creatable only by a verified-adult owner,
already chat-gated to verified-adult interactors — can be *marketed* where
adult audiences actually are: creator platforms and x-rated directories
willing to host rated profiles or their QR beacons. The venue catalog is
structural (the same pattern as the connected-apps and pack-registry
catalogs); a placement mints a printable QR beacon plus the @handle / #tag
summon refs to publish on the venue.

The age wall travels with the profile, not the venue: every discovery
surface — @handle, #tag, beacon scan, marketplace browse — resolves a
rated profile to an age-wall card unless the viewer presents an interactor
token with a verified 18+ birthdate. Venues host the pointer; QRME keeps
the gate.

Hard line, non-negotiable: adult mode is never available for a profile of
another real person (``kind: other_person``) — only ``self`` (the verified
adult owner themself) and ``fictional`` personas.
"""

from __future__ import annotations

from datetime import date

from fastapi import Request

from . import auth, db
from .common import age_of

# venue key -> card. ``hosts`` says what the venue is willing to carry:
# a linked rated profile, a printed/embedded QR beacon, or both.
VENUES: dict[str, dict] = {
    "onlyfans": {
        "name": "OnlyFans", "url": "https://onlyfans.com",
        "kind": "creator_platform", "hosts": ["profile", "beacon"],
        "blurb": "Link a rated synthetic profile from a creator page, or "
                 "embed its QR beacon in posts.",
    },
    "fansly": {
        "name": "Fansly", "url": "https://fansly.com",
        "kind": "creator_platform", "hosts": ["profile", "beacon"],
        "blurb": "Creator-platform hosting for rated profiles and their "
                 "beacons.",
    },
    "xrated_directory": {
        "name": "X-rated site directories", "url": None,
        "kind": "adult_directory", "hosts": ["beacon"],
        "blurb": "Adult sites and directories willing to carry a rated "
                 "beacon QR; the age wall still resolves on QRME's side.",
    },
}


def venue_cards() -> list[dict]:
    return [{"key": key, **venue, "age_wall": True,
             "note": "every summon of a rated profile resolves through "
                     "QRME's 18+ age wall, regardless of where the QR or "
                     "handle was found"}
            for key, venue in VENUES.items()]


def viewer_is_adult(request: Request) -> bool:
    """Whether the caller presents an interactor token with a verified 18+
    birthdate — the only thing that opens a rated discovery card."""
    who = auth.principal(request)
    if who is None or who["role"] != "interactor":
        return False
    row = db.connect().execute(
        "SELECT birthdate FROM interactors WHERE id=?",
        (who["subject_id"],)).fetchone()
    if row is None or not row["birthdate"]:
        return False
    return age_of(date.fromisoformat(row["birthdate"])) >= 18


def age_wall_card(profile_id: str) -> dict:
    """What a non-verified viewer sees instead of a rated profile card —
    existence acknowledged at direct refs, nothing else."""
    return {
        "profile_id": profile_id,
        "rated": True,
        "age_wall": True,
        "display_name": "age-restricted profile",
        "chat": None,
        "note": "18+ only — summon again with an interactor token whose "
                "verified birthdate shows 18 or older",
    }
