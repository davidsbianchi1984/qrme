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

import json
from datetime import date

from fastapi import Request

from . import auth, db, ledger
from .common import age_of

# What one verified view arriving through a venue placement earns the
# creator — simulated ad/affiliate revenue, credited to the ledger at
# resolution time. Money is simulated platform-wide; the accounting is real.
PLACEMENT_VIEW_RATE = 0.25

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


def buyer_is_adult(request: Request) -> bool:
    """Whether the caller may see and transact rated *commerce*: either a
    verified-18+ interactor, or the owner of an adult-mode profile (whose
    adult verification was proven when adult mode was enabled at
    creation)."""
    if viewer_is_adult(request):
        return True
    who = auth.principal(request)
    if who is None or who["role"] != "owner":
        return False
    row = db.connect().execute(
        "SELECT adult_mode FROM profiles WHERE id=?",
        (who["subject_id"],)).fetchone()
    return bool(row and row["adult_mode"])


def record_event(profile_id: str, beacon_id: str | None,
                 verified: bool, pdi=None) -> None:
    """Log one resolution of a rated profile on a discovery surface — the
    raw material for the owner's placement analytics. Only the outcome and
    the beacon are stored, never the viewer.

    Two side effects ride on the record:
    - a *verified* view arriving through a venue placement credits the
      creator's ledger (kind ``placement``) at ``PLACEMENT_VIEW_RATE``;
    - when a PDI vault is configured, the event is sealed there too, so a
      creator's placement history is provable through PDI's tamper-evident
      audit chain — same custody standard as the tandem exchanges.
    """
    conn = db.connect()
    event_id = db.new_id("rev")
    kind = "verified_view" if verified else "wall"
    at = db.utcnow()

    placement = None
    if beacon_id:
        placement = conn.execute(
            "SELECT id, venue FROM rated_placements WHERE beacon_id=?",
            (beacon_id,)).fetchone()

    pdi_key = None
    if pdi is not None:
        pdi_key = f"qrme/{profile_id}/rated/events/{event_id}"
        payload = {"event_id": event_id, "profile_id": profile_id,
                   "beacon_id": beacon_id, "kind": kind, "at": at}
        if placement is not None:
            payload["placement_id"] = placement["id"]
            payload["venue"] = placement["venue"]
        try:
            pdi.put(pdi_key, json.dumps(payload))
        except Exception:
            pdi_key = None   # vault unreachable — the local row still stands

    conn.execute(
        "INSERT INTO rated_events (id, profile_id, beacon_id, kind, at,"
        " pdi_key) VALUES (?,?,?,?,?,?)",
        (event_id, profile_id, beacon_id, kind, at, pdi_key))
    conn.commit()

    if verified and placement is not None:
        owner = conn.execute("SELECT owner_id FROM profiles WHERE id=?",
                             (profile_id,)).fetchone()
        if owner is not None:
            venue_name = VENUES.get(placement["venue"], {}).get(
                "name", placement["venue"])
            ledger.credit(owner["owner_id"], "placement", placement["id"],
                          PLACEMENT_VIEW_RATE,
                          memo=f"verified view via {venue_name}")


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
