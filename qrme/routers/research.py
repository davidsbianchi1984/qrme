"""Safe knowledge excursions — endpoints.

A profile's model goes and studies an unfamiliar topic, then brings general
knowledge back, without carrying the owner's private data out. See
``qrme/research.py`` for the sanitization + gather logic.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import db, i18n, letter as letter_mod, lookout, privileges, research
from ..common import profile_or_404, require_owner
from ..models import ExcursionStart, LookoutCreate

router = APIRouter()


def _exc_or_404(cid: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM excursions WHERE id=?", (cid,)).fetchone()
    if row is None:
        raise HTTPException(404, "excursion not found")
    return dict(row)


def _out(row: dict) -> dict:
    return {
        "id": row["id"],
        "profile_id": row["profile_id"],
        "topic": row["topic"],
        "brief": row["brief"],               # exactly what could leave (sanitized)
        "redactions": row["redactions"],
        "left_host": bool(row["left_host"]),
        "findings": row["findings"],
        "learned": row["learned_src"] is not None,
    }


@router.post("/profiles/{profile_id}/excursions", status_code=201)
def start_excursion(profile_id: str, body: ExcursionStart, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    # Everything outbound is sanitized and the privilege is asked for on the
    # way — both inside `research.excursion`, so a second caller cannot get
    # either wrong.
    try:
        from .. import storage as storage_mod, tiers as tiers_mod
        cid = research.excursion(
            profile_id, body.topic, body.question, body.private,
            request.app.state.cloud,
            pdi=storage_mod.vault_for(tiers_mod.plan_of_profile(profile_id),
                                      request.app.state.pdi))
    except privileges.NotChosen as exc:
        # `i18n.raised`, not `str(exc)` — see i18n.raised for what str()
        # forgets on the way.
        raise HTTPException(403, i18n.raised(exc)) from None
    return _out(_exc_or_404(cid))


@router.post("/profiles/{profile_id}/letter", status_code=201)
def write_letter(profile_id: str, request: Request) -> dict:
    """The weekly letter: the profile's week, written to its owner
    (qrme/letter.py) — composed only from what the week actually held.
    A week with nothing in it gets no letter."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return letter_mod.compose(profile_id, cloud=request.app.state.cloud,
                                  pdi=request.app.state.pdi)
    except letter_mod.LetterError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.get("/profiles/{profile_id}/letters")
def letter_shelf(profile_id: str, request: Request) -> list[dict]:
    """Past weekly letters, newest first, each carrying the digest the
    words were made from."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return letter_mod.shelf(profile_id)


@router.post("/profiles/{profile_id}/lookout", status_code=201)
def plant_lookout(profile_id: str, body: LookoutCreate,
                  request: Request) -> dict:
    """Keep an eye on a page: one standing appointment in the vault
    (qrme/lookout.py), whose resident re-fetches and re-seals the current
    capture on the interval — the profile then answers from the capture.
    Behind the same `study_the_web` privilege the excursions ask for."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    from .. import storage as storage_mod, tiers as tiers_mod
    try:
        out = lookout.plant(
            profile_id, body.url, body.every_hours,
            pdi=storage_mod.vault_for(tiers_mod.plan_of_profile(profile_id),
                                      request.app.state.pdi))
    except privileges.NotChosen as exc:
        raise HTTPException(403, i18n.raised(exc)) from None
    if not out["planted"]:
        raise HTTPException(422, out["why"])
    return out


@router.get("/profiles/{profile_id}/lookout")
def list_lookouts(profile_id: str, request: Request) -> dict:
    """This profile's lookouts, with what the vault says about each —
    `readable: false` when the tandem could not be asked. The real
    vault: reads keep `app.state.pdi`."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return lookout.watches(profile_id, pdi=request.app.state.pdi)


@router.get("/profiles/{profile_id}/lookout/{lookout_id}/page")
def read_lookout(profile_id: str, lookout_id: str,
                 request: Request) -> dict:
    """The current capture, read back from the seal."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    out = lookout.page(profile_id, lookout_id,
                       pdi=request.app.state.pdi)
    if out is None:
        raise HTTPException(404, "no such lookout")
    return out


@router.delete("/profiles/{profile_id}/lookout/{lookout_id}")
def drop_lookout(profile_id: str, lookout_id: str,
                 request: Request) -> dict:
    """Stop the watching the whole way: the appointment, the seal, the
    row — in that order. The real vault, like every delete."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    out = lookout.drop(profile_id, lookout_id, pdi=request.app.state.pdi)
    if out is None:
        raise HTTPException(404, "no such lookout")
    return out


@router.get("/profiles/{profile_id}/excursions")
def list_excursions(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM excursions WHERE profile_id=?"
        " ORDER BY created_at, rowid", (profile_id,)).fetchall()
    return [_out(dict(r)) for r in rows]


@router.get("/excursions/{cid}")
def get_excursion(cid: str, request: Request) -> dict:
    row = _exc_or_404(cid)
    require_owner(row["profile_id"], request)
    return _out(row)


@router.post("/excursions/{cid}/learn", status_code=201)
def learn(cid: str, request: Request) -> dict:
    """Fold the findings into the profile as a learned ``knowledge`` source —
    the model 'lets it back in'. The local model then uses it going forward."""
    row = _exc_or_404(cid)
    require_owner(row["profile_id"], request)
    if not row["findings"]:
        raise HTTPException(409, "this excursion has no findings to learn")
    if row["learned_src"]:
        return {"source_id": row["learned_src"], "already_learned": True}
    pdi = request.app.state.pdi
    conn = db.connect()
    item_id = db.new_id("src")
    title = f"Learned: {row['topic']}"
    content, pdi_key = row["findings"], None
    if pdi is not None and content:
        pdi_key = f"qrme/{row['profile_id']}/sources/{item_id}"
        pdi.put(pdi_key, json.dumps({"content": content}))
        content = None
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, created_at) VALUES (?,?,'knowledge',?,?,?,?)",
        (item_id, row["profile_id"], title, content, pdi_key, db.utcnow()),
    )
    conn.execute("UPDATE excursions SET learned_src=? WHERE id=?", (item_id, cid))
    conn.commit()
    return {"source_id": item_id, "already_learned": False,
            "note": "findings folded into the profile; the local model now uses them"}
