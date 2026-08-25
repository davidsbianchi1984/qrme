"""Summoning: @handles, #tags, and QR beacons.

A synthetic profile can be reached three ways:

- ``@handle`` — a claimed, unique handle for direct summoning;
- ``#tag``    — topical summoning through marketplace tags;
- **beacon**  — a profile *left behind* somewhere physical: a placed QR
  anchor (bench, storefront, memorial plaque) whose code resolves to the
  profile. Scans are counted, beacons can be picked back up, and a beacon
  for a departed profile resolves as a memorial rather than a chat.

All summon responses are public discovery cards — display info only, never
persona internals; anonymous profiles stay anonymous.
"""

from __future__ import annotations

import io
import json
import os

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse

from .. import avatars, db, identity, landing, rated
from ..common import profile_or_404, require_owner
from ..models import BeaconCreate, HandleSet, RatedPlacementCreate
from .. import i18n

router = APIRouter()


def _absolute(asset: str | None) -> str | None:
    """Root-relative asset paths become absolute against the public base."""
    if not asset or not asset.startswith("/"):
        return asset
    return f"{_public_base()}{asset}"


def _public_base() -> str:
    return os.environ.get("QRME_PUBLIC_URL", "https://qrme.app").rstrip("/")


_STATUS_NOTE = {
    "departed": "this profile has departed; its memory remains with those "
                "who knew it",
    "restricted": "this profile is restricted pending an objection review",
    "terminated": "this profile has been terminated",
}


def _card(profile: dict, handle: str | None = None) -> dict:
    """Public summon card — never persona internals."""
    # Only an active profile is chat-reachable from a public summon; a
    # restricted profile's public surfaces are off, and departed/terminated
    # profiles never chat.
    reachable = profile["status"] == "active"
    return {
        "profile_id": profile["id"],
        "display_name": identity.shown_name(profile),
        "handle": f"@{handle}" if handle else _handle_of(profile["id"]),
        "purpose": profile["purpose"],
        "status": profile["status"],
        "rated": bool(profile["adult_mode"]),
        "chat": (f"/profiles/{profile['id']}/chat" if reachable else None),
        "note": _STATUS_NOTE.get(profile["status"]),
    }


def _gated_card(profile: dict, request: Request,
                handle: str | None = None) -> dict:
    """The summon card, behind the age wall when the profile is rated: a
    viewer without a verified-18+ interactor token gets the wall, never
    the card. The wall travels with the profile — it holds no matter where
    the @handle, #tag, or beacon QR was published."""
    if profile["adult_mode"] and not rated.viewer_is_adult(request):
        return rated.age_wall_card(profile["id"])
    return _card(profile, handle)


def _handle_of(profile_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT handle FROM handles WHERE profile_id=?", (profile_id,)
    ).fetchone()
    return f"@{row['handle']}" if row else None


# -- @handles ----------------------------------------------------------------

def claim_handle(profile_id: str, body: HandleSet) -> dict:
    """Give this profile the name it answers to.

    Split from the route below so the seeders can call it. They are minting
    a profile and naming it in the same breath, on this deployment's own
    behalf, and there is no owner to be yet — the token does not exist until
    the profile does.
    """
    profile_or_404(profile_id)
    handle = body.handle.lstrip("@").lower()
    conn = db.connect()
    taken = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                         (handle,)).fetchone()
    if taken and taken["profile_id"] != profile_id:
        raise HTTPException(409, i18n.fill(i18n.HANDLE_CLAIMED, handle=handle))
    conn.execute("DELETE FROM handles WHERE profile_id=?", (profile_id,))
    conn.execute(
        "INSERT INTO handles (handle, profile_id, created_at) VALUES (?,?,?)",
        (handle, profile_id, db.utcnow()),
    )
    conn.commit()
    return {"profile_id": profile_id, "handle": f"@{handle}",
            "summon": f"/summon?ref=@{handle}"}


@router.put("/profiles/{profile_id}/handle")
def put_handle(profile_id: str, body: HandleSet, request: Request) -> dict:
    """Claim the name this profile answers to. Owner only.

    It took no credential at all, and the damage was not that somebody could
    give a profile a second name — it is the `DELETE` above. A stranger could
    replace the handle a profile had published, so `@rosa` stopped resolving
    and `@notrosa` resolved to Rosa. Every printed reference, shared link and
    beacon that pointed at her by name went dead at once, and the name she now
    answered to was chosen by whoever did it.

    The three routes immediately below this one were given exactly this check
    in an earlier pass, and `place_beacon` states the reason in words that fit
    here without changing: *it was anybody's, which meant a stranger could
    print stickers pointing at somebody else's profile.* This route was
    missed.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return claim_handle(profile_id, body)


# -- beacons: leave a profile behind -----------------------------------------

@router.post("/profiles/{profile_id}/beacons", status_code=201)
def place_beacon(profile_id: str, body: BeaconCreate,
                 request: Request) -> dict:
    """Leave this profile somewhere. Owner only.

    It was anybody's, which meant a stranger could print stickers pointing at
    somebody else's profile, in places its owner never chose and cannot see.
    Where a profile is left is a decision about the profile — a recovery
    sponsor's code belongs at a meeting and not on a billboard — and the owner
    is the only person entitled to make it.
    """
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    beacon_id = db.new_id("bcn")
    room_id = None
    if body.mode == "room" and profile["adult_mode"]:
        # Documented since the feature shipped and never enforced: "rated
        # placements stay one-to-one". A shared room behind an adult QR at a
        # public venue is a different product with different moderation
        # questions — strangers who scanned a sticker on a wall, in one room
        # together, with rated material between them — and it was reachable by
        # setting a flag. Refused rather than silently downgraded to `chat`,
        # because somebody who asked for a room and got a private thread would
        # not find out until the fortieth person was talking to themselves.
        raise HTTPException(
            422, "a rated profile is placed one-to-one. A shared room behind "
                 "an adult code in a public place is a different product with "
                 "different moderation questions, not a flag on this one")
    if body.mode == "room":
        # One room, minted with the profile in it, that every scanner joins.
        # The people who found the same sticker end up talking to the profile
        # together rather than each in their own private thread.
        room_id = db.new_id("room")
        conn.execute(
            "INSERT INTO rooms (id, topic, channel, status, created_at)"
            " VALUES (?,?,'chat','active',?)",
            (room_id, body.topic or body.label, db.utcnow()))
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?, 'profile', ?)", (room_id, profile_id))
    conn.execute(
        "INSERT INTO beacons (id, profile_id, label, location, room_id, scans, active,"
        " created_at) VALUES (?,?,?,?,?,0,1,?)",
        (beacon_id, profile_id, body.label, body.location, room_id,
         db.utcnow()),
    )
    conn.commit()
    return {
        "id": beacon_id, "label": body.label, "location": body.location,
        # summon_url is unchanged: the JSON surface clients already read.
        # scan_url is the page a phone camera should land on, and is what the
        # printed QR encodes — sharing or printing that one is the point.
        "summon_url": f"{_public_base()}/summon?ref={beacon_id}",
        "scan_url": f"{_public_base()}/b/{beacon_id}",
        "mode": body.mode,
        "room_id": room_id,
        "qr_svg": f"/beacons/{beacon_id}/qr.svg",
    }


@router.get("/profiles/{profile_id}/beacons")
def list_beacons(profile_id: str, request: Request) -> list[dict]:
    """Every place this profile has been left. Owner only.

    The rows carry `label` and `location` — free text like "Rosa's garden
    bench" or "the back table at the Tuesday meeting". That is a list of
    physical places associated with a person, and it was readable by anybody
    with the profile id. Scanning one code told you where all the others were.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM beacons WHERE profile_id=? ORDER BY created_at, rowid",
        (profile_id,)).fetchall()
    return [{**dict(r), "active": bool(r["active"])} for r in rows]


@router.delete("/beacons/{beacon_id}")
def pick_up_beacon(beacon_id: str, request: Request) -> dict:
    """Pick a beacon back up: the placed QR stops summoning. Owner only.

    Unauthenticated, this was a way to switch off somebody else's printed
    stickers — every code they had put up going dead at once, with the paper
    still on the wall and nothing to see wrong with it.
    """
    conn = db.connect()
    row = conn.execute("SELECT profile_id FROM beacons WHERE id=?",
                       (beacon_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "beacon not found")
    require_owner(row["profile_id"], request)
    conn.execute("UPDATE beacons SET active=0 WHERE id=?", (beacon_id,))
    conn.commit()
    return {"id": beacon_id, "active": False}


@router.get("/beacons/{beacon_id}/qr.svg")
def beacon_qr(beacon_id: str) -> Response:
    """The printable QR code for a placed beacon."""
    row = db.connect().execute("SELECT id FROM beacons WHERE id=?",
                               (beacon_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "beacon not found")
    import segno

    buf = io.BytesIO()
    segno.make(f"{_public_base()}/b/{beacon_id}",
               error="q").save(buf, kind="svg", scale=8, border=2,
                               dark="#161840", light="#F4E3C8")
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


# -- the scan surface --------------------------------------------------------

@router.get("/b/{beacon_id}", response_class=HTMLResponse)
def scan_beacon(beacon_id: str, request: Request) -> HTMLResponse:
    """Where a placed QR actually points.

    A phone's camera app can only open a URL, so this is what "aim it at the
    sticker and the profile appears" resolves to in practice: one
    self-contained page that reveals the portrait immediately. Same beacon,
    same scan count, same age wall as ``/summon?ref=`` — that stays the JSON
    surface for clients that want data.
    """
    conn = db.connect()
    beacon = conn.execute("SELECT * FROM beacons WHERE id=?",
                          (beacon_id,)).fetchone()
    if beacon is None:
        return HTMLResponse(landing.gone(), status_code=404)
    if not beacon["active"]:
        return HTMLResponse(landing.gone(), status_code=410)

    conn.execute("UPDATE beacons SET scans = scans + 1 WHERE id=?", (beacon_id,))
    conn.commit()

    row = conn.execute("SELECT * FROM profiles WHERE id=?",
                       (beacon["profile_id"],)).fetchone()
    if row is None:
        return HTMLResponse(landing.gone("profile"), status_code=404)
    profile = dict(row)

    if profile["adult_mode"]:
        # A stranger scanning a sticker never has a token, so this is the
        # ordinary path for a rated beacon, not the exception.
        rated.record_event(profile["id"], beacon["id"],
                           rated.viewer_is_adult(request),
                           pdi=request.app.state.pdi)
        if not rated.viewer_is_adult(request):
            return HTMLResponse(landing.age_wall(), status_code=200)

    if profile["status"] != "active":
        return HTMLResponse(landing.gone("profile"), status_code=410)

    return HTMLResponse(landing.profile_page(
        profile, _public_base(), beacon["label"], beacon["room_id"]))


@router.get("/b/{beacon_id}/card")
def beacon_card(beacon_id: str, request: Request) -> dict:
    """The smallest thing an in-camera overlay needs.

    The app draws this *over the sticker in the live viewfinder* — nobody has
    navigated anywhere, and the camera is running while it waits. So this is
    deliberately tiny: who it is, one line of portrait, and the mark. Not the
    full summon card, which carries chat URLs and status notes an overlay has
    no use for.

    A scan through the overlay counts the same as opening the page. It is the
    same person finding the same sticker; the only difference is that they
    never had to leave the camera.
    """
    conn = db.connect()
    beacon = conn.execute("SELECT * FROM beacons WHERE id=?",
                          (beacon_id,)).fetchone()
    if beacon is None or not beacon["active"]:
        raise HTTPException(404, "nothing answers to that code")

    conn.execute("UPDATE beacons SET scans = scans + 1 WHERE id=?", (beacon_id,))
    conn.commit()

    profile = profile_or_404(beacon["profile_id"])
    if profile["adult_mode"]:
        rated.record_event(profile["id"], beacon["id"],
                           rated.viewer_is_adult(request),
                           pdi=request.app.state.pdi)
        if not rated.viewer_is_adult(request):
            # The overlay must be able to render the wall without ever holding
            # the name or the portrait, so none of it is sent.
            return {"age_wall": True, "rated": True,
                    "note": "18+ — open in QRME with a verified adult account"}
    if profile["status"] != "active":
        raise HTTPException(410, "this profile no longer answers")

    art = avatars.render(profile["id"])
    name = (identity.anonymous_name(profile["id"]) if profile["anonymous"]
            else profile["display_name"])
    return {
        "profile_id": profile["id"],
        "display_name": name,
        # The mark travels with the card, so an overlay cannot draw the face
        # without also having been handed the disclosure to draw with it.
        "watermark": art["watermark"]["line"],
        # Absolute, because the overlay is a native client building a URL —
        # a root-relative path is a valid href in a browser and a broken URL
        # everywhere else.
        "portrait": _absolute(art["asset"]),
        # Whether the disclosure is already in the image. QRME's own overlays
        # draw their badge either way — theirs carries the profile's designed
        # label and is real text — but a surface QRME does not control needs to
        # know whether compositing is mandatory or merely additive.
        "portrait_marked": art["asset_marked"],
        "label": beacon["label"],
        "shared_room": beacon["room_id"],
        "open_url": f"{_public_base()}/b/{beacon_id}",
        "age_wall": False,
    }


# -- the summon endpoint -----------------------------------------------------

@router.get("/summon")
def summon(ref: str, request: Request) -> dict:
    """Resolve @handle, #tag, or a beacon token to summonable profiles.
    Rated (18+) profiles resolve through the age wall: direct refs (@handle,
    beacon) answer with a wall card, and #tag browse omits them entirely,
    unless the viewer presents a verified-18+ interactor token."""
    conn = db.connect()

    if ref.startswith("@"):
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (ref[1:].lower(),)).fetchone()
        if row is None:
            raise HTTPException(404, i18n.fill(i18n.NO_PROFILE_ANSWERS, handle=ref))
        profile = profile_or_404(row["profile_id"])
        if profile["adult_mode"]:
            rated.record_event(profile["id"], None,
                               rated.viewer_is_adult(request),
                               pdi=request.app.state.pdi)
        return {"type": "handle", "ref": ref,
                "profile": _gated_card(profile, request)}

    if ref.startswith("#"):
        tag = ref[1:].lower()
        adult_viewer = rated.viewer_is_adult(request)
        rows = conn.execute(
            "SELECT m.profile_id, m.tags FROM marketplace m"
            " JOIN profiles p ON p.id = m.profile_id"
            " ORDER BY m.listed_at DESC").fetchall()
        cards = []
        for r in rows:
            if tag not in [t.lower() for t in json.loads(r["tags"])]:
                continue
            profile = profile_or_404(r["profile_id"])
            # Browse never even hints at rated profiles to a non-verified
            # viewer — a list is not a direct ref.
            if profile["adult_mode"] and not adult_viewer:
                continue
            cards.append(_card(profile))
        return {"type": "tag", "ref": ref, "profiles": cards}

    beacon = conn.execute("SELECT * FROM beacons WHERE id=?", (ref,)).fetchone()
    if beacon is None:
        raise HTTPException(404, "nothing answers to that reference")
    if not beacon["active"]:
        raise HTTPException(410, "this beacon has been picked up")
    conn.execute("UPDATE beacons SET scans = scans + 1 WHERE id=?", (ref,))
    conn.commit()
    profile = profile_or_404(beacon["profile_id"])
    if profile["adult_mode"]:
        rated.record_event(profile["id"], beacon["id"],
                           rated.viewer_is_adult(request),
                           pdi=request.app.state.pdi)
    return {"type": "beacon", "ref": ref,
            "label": beacon["label"], "location": beacon["location"],
            "scans": beacon["scans"] + 1,
            "profile": _gated_card(profile, request)}


# -- rated (18+) placement: marketing at adult venues ------------------------

@router.get("/venues")
def rated_venues() -> list[dict]:
    """Adult venues willing to host rated profiles or their beacons. The
    catalog is structural; the age wall always resolves on QRME's side."""
    return rated.venue_cards()


@router.post("/profiles/{profile_id}/placements", status_code=201)
def place_rated(profile_id: str, body: RatedPlacementCreate,
                request: Request) -> dict:
    """Owner-only: market an adult-mode profile at an adult venue. Mints a
    beacon (printable / embeddable QR) and returns the summon refs to
    publish there — every one of which resolves through the age wall."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    venue = rated.VENUES.get(body.venue)
    if venue is None:
        raise HTTPException(404, "unknown venue")
    if not profile["adult_mode"]:
        raise HTTPException(
            422, "only adult-mode profiles are placed at adult venues")
    conn = db.connect()
    beacon_id = db.new_id("bcn")
    # Rated placements stay one-to-one. A shared room behind an 18+ QR at a
    # public venue is a different product with different moderation
    # questions, and is not something to acquire by accident.
    label = body.label or f"{venue['name']} placement"
    conn.execute(
        "INSERT INTO beacons (id, profile_id, label, location, scans,"
        " active, created_at) VALUES (?,?,?,?,0,1,?)",
        (beacon_id, profile_id, label, venue["name"], db.utcnow()))
    placement_id = db.new_id("plc")
    conn.execute(
        "INSERT INTO rated_placements (id, profile_id, venue, beacon_id,"
        " label, created_at) VALUES (?,?,?,?,?,?)",
        (placement_id, profile_id, body.venue, beacon_id, label,
         db.utcnow()))
    conn.commit()
    return {
        "placement_id": placement_id,
        "venue": {"key": body.venue, "name": venue["name"],
                  "url": venue["url"], "hosts": venue["hosts"]},
        "beacon_id": beacon_id,
        # summon_url is unchanged: the JSON surface clients already read.
        # scan_url is the page a phone camera should land on, and is what the
        # printed QR encodes — sharing or printing that one is the point.
        "summon_url": f"{_public_base()}/summon?ref={beacon_id}",
        "scan_url": f"{_public_base()}/b/{beacon_id}",
        "qr_svg": f"/beacons/{beacon_id}/qr.svg",
        "handle": _handle_of(profile_id),
        "rated": True,
        "note": "publish the QR or refs at the venue; every scan and summon "
                "resolves through QRME's 18+ age wall",
    }


@router.get("/profiles/{profile_id}/placements")
def list_placements(profile_id: str, request: Request) -> list[dict]:
    """Owner view: where this rated profile is marketed, with scan counts."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT pl.id, pl.venue, pl.beacon_id, pl.label, pl.created_at,"
        " b.scans, b.active FROM rated_placements pl JOIN beacons b"
        " ON b.id = pl.beacon_id WHERE pl.profile_id=?"
        " ORDER BY pl.created_at, pl.rowid", (profile_id,)).fetchall()
    return [{**dict(r), "active": bool(r["active"]),
             "venue_name": rated.VENUES.get(r["venue"], {}).get("name",
                                                               r["venue"])}
            for r in rows]


@router.get("/profiles/{profile_id}/placements/analytics")
def placement_analytics(profile_id: str, request: Request) -> dict:
    """Owner-only: what each venue earns. Per-placement scan counts split
    into walled vs. verified resolutions with a daily trend, plus the
    profile-level funnel — scans → verified views → unique chatters — so a
    creator sees which venue converts. Counts and rates only; viewers are
    never identified."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()

    def _counts(where: str, params: tuple) -> tuple[int, int]:
        row = conn.execute(
            f"SELECT SUM(kind='wall') AS walled,"
            f" SUM(kind='verified_view') AS verified"
            f" FROM rated_events WHERE {where}", params).fetchone()
        return row["walled"] or 0, row["verified"] or 0

    venues = []
    for pl in conn.execute(
            "SELECT pl.*, b.scans, b.active FROM rated_placements pl"
            " JOIN beacons b ON b.id = pl.beacon_id WHERE pl.profile_id=?"
            " ORDER BY pl.created_at, pl.rowid", (profile_id,)).fetchall():
        walled, verified = _counts("beacon_id=?", (pl["beacon_id"],))
        by_day = [dict(r) for r in conn.execute(
            "SELECT substr(at, 1, 10) AS day, COUNT(*) AS scans"
            " FROM rated_events WHERE beacon_id=? GROUP BY day"
            " ORDER BY day", (pl["beacon_id"],)).fetchall()]
        venues.append({
            "placement_id": pl["id"], "venue": pl["venue"],
            "venue_name": rated.VENUES.get(pl["venue"], {}).get(
                "name", pl["venue"]),
            "label": pl["label"], "active": bool(pl["active"]),
            "scans": pl["scans"], "walled": walled, "verified": verified,
            "by_day": by_day,
        })

    # Direct refs (@handle summons) have no beacon — they are their own row.
    walled_direct, verified_direct = _counts(
        "profile_id=? AND beacon_id IS NULL", (profile_id,))
    total_walled, total_verified = _counts("profile_id=?", (profile_id,))
    chatters = conn.execute(
        "SELECT COUNT(DISTINCT interactor_id) AS n FROM messages"
        " WHERE profile_id=? AND role='interactor'",
        (profile_id,)).fetchone()["n"]
    total = total_walled + total_verified
    return {
        "profile_id": profile_id,
        "venues": venues,
        "direct": {"walled": walled_direct, "verified": verified_direct},
        "funnel": {
            "resolutions": total,
            "verified_views": total_verified,
            "unique_chatters": chatters,
            "verified_rate": (round(total_verified / total, 2)
                              if total else None),
            "chat_rate": (round(chatters / total_verified, 2)
                          if total_verified else None),
        },
    }


@router.get("/profiles/{profile_id}/placements/custody")
def placement_custody(profile_id: str, request: Request) -> dict:
    """Owner-only: the profile's rated-event custody — every event sealed
    into the PDI vault (key list, newest first) plus whether PDI's
    tamper-evident audit chain verifies intact. 409 when no vault is
    configured — custody can't be claimed without one."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    pdi = request.app.state.pdi
    if pdi is None:
        raise HTTPException(
            409, "no PDI vault configured (set QRME_PDI_URL / QRME_PDI_TOKEN)")
    rows = db.connect().execute(
        "SELECT id, kind, at, pdi_key FROM rated_events"
        " WHERE profile_id=? AND pdi_key IS NOT NULL"
        " ORDER BY at DESC, rowid DESC", (profile_id,)).fetchall()
    return {
        "profile_id": profile_id,
        "records": [dict(r) for r in rows],
        "count": len(rows),
        "chain_intact": pdi.audit_verify(),
        "note": "each sealed event is provable through PDI's audit chain — "
                "the same custody standard as tandem exchanges",
    }


@router.delete("/placements/{placement_id}")
def remove_placement(placement_id: str, request: Request) -> dict:
    """Owner-only: withdraw a placement — its beacon stops summoning."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM rated_placements WHERE id=?",
                       (placement_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "placement not found")
    require_owner(row["profile_id"], request)
    conn.execute("UPDATE beacons SET active=0 WHERE id=?",
                 (row["beacon_id"],))
    conn.execute("DELETE FROM rated_placements WHERE id=?", (placement_id,))
    conn.commit()
    return {"placement_id": placement_id, "removed": True,
            "beacon_id": row["beacon_id"], "beacon_active": False}
