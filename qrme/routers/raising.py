"""Raise — the fourth kind's own doors. Mounted at ``/raise``.

The creation door records the three things a raised life needs from
birth — a stage, a preset, a temperament seed — mints the profile with
``kind="raised"``, and writes the Album's first entry. Everything after
that is made between the guardian and the character: the teach door is
where words, lessons and answers land, the Album is the living timeline,
and the switches door is where the preset's bundle gets rewired (with
the mortality warning said out loud every time that one turns on).

The guardian is the owner token — raising is an owner's act, and the
routes say "guardian" because that is what the owner of a raised life
is called in this service.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .. import auth, db, i18n, raising, terms, tiers
from ..common import age_of, profile_or_404, require_owner
from ..models import RaiseCreate

router = APIRouter()


@router.get("/raise/doors")
def doors() -> dict:
    """What a life can start as — the stages, the four preset doors and
    the bundle each one is, and the temperament axes. Public: this is
    the creation screen's vocabulary, readable before any account."""
    return {
        "stages": list(raising.STAGES),
        "presets": {name: dict(bundle)
                    for name, bundle in raising.PRESETS.items()},
        "temperament_axes": list(raising.TEMPERAMENT_AXES),
        "mortality_warning": i18n.tr_public(raising.MORTALITY_WARNING, "en"),
    }


@router.post("/raise", status_code=201,
             dependencies=[Depends(auth.require_signup_key)])
def begin(body: RaiseCreate) -> dict:
    """A life begins. The profile is minted with the fourth kind, the
    character row holds the stage/preset/seed, and the Album opens.

    Childhood stages are pinned to the strictest maturity at the row —
    the law, not a setting — and the persona is seeded with the honest
    truth of the stage rather than a typed backstory: a raised
    character has no script, which is the whole pitch.
    """
    if not body.terms_consent:
        raise HTTPException(
            403, "acceptance of the Terms of Service is required to create "
                 "a profile (GET /terms)")
    owner_age = age_of(body.verification.birthdate)
    if owner_age < 18 and not body.verification.guardian_consent:
        raise HTTPException(403,
                            "owners under 18 require parent/guardian consent")
    try:
        # Checked BEFORE the profile is minted, so a refused creation
        # leaves no orphan row behind. The engine words the refusals.
        raising.validate(body.stage, body.preset, body.temperament)
    except raising.RaiseError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None

    profile_id = db.new_id("prf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " demographics, sources, anonymous, adult_mode, interaction_scope,"
        " moderation_mode, aging_enabled, base_age, consent_basis,"
        " consent_attestor, successor_owner, purpose, maturity,"
        " cloud_contribution, terms_version, terms_accepted_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            profile_id, body.owner_id, "raised", body.display_name,
            # No backstory pack, no script: the persona is one honest
            # sentence and the raising writes the rest.
            "A raised character: grown through interaction, starting from "
            "almost nothing. Everything they know was taught.",
            json.dumps({}), json.dumps([]), 0, 0, "private", "auto",
            0, None, None, None, None, None,
            # The law: a childhood runs strict whatever anybody types.
            "strict" if body.stage in raising.CHILDHOOD else "balanced",
            0, terms.TERMS_VERSION, db.utcnow(), db.utcnow(),
        ),
    )
    conn.commit()
    try:
        character = raising.begin(profile_id, body.owner_id, body.stage,
                                  body.preset, body.temperament)
    except raising.RaiseError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None
    if body.language:
        if body.language not in i18n.SUPPORTED:
            raise HTTPException(
                422, i18n.fill(i18n.MUST_BE_ONE_OF, field="language",
                               choices=", ".join(i18n.SUPPORTED)))
        i18n.set_language(profile_id, body.language)
    from ..routers.profiles import _enrol
    _enrol(body.owner_id, None)
    token = auth.issue("owner", profile_id)
    return {"profile_id": profile_id, "owner_token": token,
            "display_name": body.display_name, "kind": "raised",
            "character": character,
            "membership": tiers.membership(body.owner_id)}


@router.get("/raise/{profile_id}")
def read(profile_id: str, request: Request) -> dict:
    """The character as they stand: stage, milestones, switches, and how
    far the next door is. Guardian only — a childhood is guardian-only
    by law, and an adult's raising is still its guardian's book."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return raising.character(profile_id)
    except raising.RaiseError as exc:
        raise HTTPException(404, i18n.raised(exc)) from None


@router.get("/raise/{profile_id}/album")
def album(profile_id: str, request: Request) -> dict:
    """The living timeline, oldest first: the first entry, every word
    and lesson, every stage door — append-only, so nobody deletes a
    life they watched grow."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return {"profile_id": profile_id, "entries": raising.album(profile_id)}


class VisitIn(BaseModel):
    #: The lived day to stand on; null comes back to the present.
    sim_day: int | None = Field(None, ge=1)


@router.post("/raise/{profile_id}/visit")
def visit(profile_id: str, body: VisitIn, request: Request) -> dict:
    """Rewind as presence: step back to a lived day and the character
    speaks as they were, knowing only what the record held by then.
    Read-only — teaching and growth wait for the present — and refused
    outright on a sealed timeline, which is lived forward only."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return raising.visit(profile_id, profile["owner_id"], body.sim_day)
    except raising.RaiseError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


class ForwardIn(BaseModel):
    #: Simulated days to live while you're away. Capped at thirty per
    #: jump everywhere but the unlocked (sandbox) time controls.
    days: int = Field(..., ge=1)


@router.post("/raise/{profile_id}/forward")
def forward(profile_id: str, body: ForwardIn, request: Request) -> dict:
    """Fast-forward: days lived from the record alone — practicing what
    was taught, saving questions for you, quiet days said honestly.
    Growth accrues at a discount: your attention stays the main
    ingredient, so away time never replaces the relationship."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return raising.forward(profile_id, profile["owner_id"], body.days)
    except raising.RaiseError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


class BranchIn(BaseModel):
    #: The lived day the new life grows from, and its own name.
    sim_day: int = Field(..., ge=1)
    display_name: str = Field(..., min_length=1, max_length=80)


@router.post("/raise/{profile_id}/branch", status_code=201)
def branch(profile_id: str, body: BranchIn, request: Request) -> dict:
    """Rewind as a second life: the record up to a lived day, copied
    into a NEW character raised differently from there. The original is
    never overwritten — the branch stands beside it, and the law rides
    along (a childhood day branched is a childhood raised: family
    forever). Unlocked time controls only."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        # Checked BEFORE the profile is minted — the creation door's
        # no-orphan discipline, kept by the branch door too.
        raising.branch_check(profile_id, profile["owner_id"], body.sim_day)
    except raising.RaiseError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None

    new_id = db.new_id("prf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " demographics, sources, anonymous, adult_mode, interaction_scope,"
        " moderation_mode, aging_enabled, maturity, cloud_contribution,"
        " terms_version, terms_accepted_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (new_id, profile["owner_id"], "raised", body.display_name,
         "A raised character: grown through interaction, starting from "
         "almost nothing. Everything they know was taught.",
         json.dumps({}), json.dumps([]), 0, 0, "private", "auto", 0,
         "balanced", 0, profile["terms_version"],
         db.utcnow(), db.utcnow()))
    conn.commit()
    made = raising.branch(profile_id, profile["owner_id"], body.sim_day,
                          new_id)
    # The law at the row, same as the creation door: a branch standing
    # in (or grown from) a childhood runs strict whatever anybody types.
    if (made["stage"] in raising.CHILDHOOD
            or made["started_stage"] in raising.CHILDHOOD):
        conn.execute("UPDATE profiles SET maturity='strict' WHERE id=?",
                     (new_id,))
        conn.commit()
    token = auth.issue("owner", new_id)
    return {"profile_id": new_id, "owner_token": token,
            "display_name": body.display_name, "kind": "raised",
            "character": made}


class TeachIn(BaseModel):
    #: word | lesson | answer — a word taught, a lesson passed, or an
    #: answer to one of their questions.
    teaching: str = Field(..., max_length=20)
    what: str = Field(..., max_length=400)


@router.post("/raise/{profile_id}/teach", status_code=201)
def teach(profile_id: str, body: TeachIn, request: Request) -> dict:
    """What you teach it, it knows: the lesson lands in the Album,
    weighs into the milestones, and — when a door's cost is met — opens
    the next stage, earned rather than aged into."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return raising.teach(profile_id, profile["owner_id"],
                             body.teaching, body.what)
    except raising.RaiseError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


class SwitchesIn(BaseModel):
    changes: dict = Field(default_factory=dict)


@router.patch("/raise/{profile_id}/switches")
def switches(profile_id: str, body: SwitchesIn, request: Request) -> dict:
    """Rewire the preset's bundle — every mechanic is a switch, and the
    only non-switches are the law. Mortality turning ON returns the
    worded warning with the change; turning it OFF is always allowed."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        out = raising.set_switches(profile_id, profile["owner_id"],
                                   body.changes)
    except raising.RaiseError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None
    if out["warning"]:
        out["warning"] = i18n.tr_public(
            out["warning"], i18n.effective_language(profile_id))
    return out
