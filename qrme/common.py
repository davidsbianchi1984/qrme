"""Shared request helpers used across the API routers."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, Request

from . import auth, db, persona
from .models import MessageOut, ProfileOut


def age_of(birthdate: date) -> int:
    today = datetime.now().date()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


def profile_or_404(profile_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "profile not found")
    return dict(row)


def require_owner(profile_id: str, request: Request) -> None:
    """Gate an owner-control endpoint: the caller must hold the profile's
    owner token."""
    auth.require(request, "owner", profile_id)


def require_interactor(interactor_id: str, request: Request) -> None:
    """Gate a per-interactor private endpoint: the caller must hold that
    interactor's token."""
    auth.require(request, "interactor", interactor_id)


def require_owner_or_interactor(profile_id: str, interactor_id: str,
                                request: Request) -> None:
    """Gate a shared per-interactor surface (a conversation's memory): either
    the profile's owner or that interactor may access it."""
    who = auth.principal(request)
    if who == {"role": "owner", "subject_id": profile_id}:
        return
    if who == {"role": "interactor", "subject_id": interactor_id}:
        return
    if who is None:
        raise HTTPException(401, "authentication required")
    raise HTTPException(403, "not authorized for this resource")


def interactor_or_404(interactor_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM interactors WHERE id=?", (interactor_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "interactor not found")
    return dict(row)


def get_active_handoff(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM active_handoffs WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id)).fetchone()
    return dict(row) if row else None


def set_active_handoff(profile_id: str, interactor_id: str, domain: str,
                       specialist_profile_id: str) -> None:
    conn = db.connect()
    conn.execute(
        "INSERT INTO active_handoffs (profile_id, interactor_id, domain,"
        " specialist_profile_id, since) VALUES (?,?,?,?,?)"
        " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
        " domain=excluded.domain,"
        " specialist_profile_id=excluded.specialist_profile_id,"
        " since=excluded.since",
        (profile_id, interactor_id, domain, specialist_profile_id, db.utcnow()),
    )
    conn.commit()


def clear_active_handoff(profile_id: str, interactor_id: str) -> None:
    conn = db.connect()
    conn.execute(
        "DELETE FROM active_handoffs WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id))
    conn.commit()


def _in_quiet_hours(interactor: dict, now: datetime) -> bool:
    """Whether the recipient's quiet-hours window covers the current UTC hour.
    A window that wraps midnight (start > end) is handled."""
    start, end = interactor.get("quiet_start"), interactor.get("quiet_end")
    if start is None or end is None:
        return False
    hour = now.hour
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end        # overnight window


def proactive_gate(profile: dict, interactor: dict) -> str | None:
    """Anti-spam gate for unprompted outreach. Returns a rejection reason, or
    None when outreach is allowed. Three rules (see lifecycle-and-consent.md):
    a per-relationship rate cap, the recipient's quiet hours, and suppression
    until the recipient has replied at least once."""
    now = datetime.now(timezone.utc)
    if _in_quiet_hours(interactor, now):
        return "the recipient's quiet hours are in effect"
    row = db.connect().execute(
        "SELECT last_outreach_at, awaiting_reply FROM proactive_state"
        " WHERE profile_id=? AND interactor_id=?",
        (profile["id"], interactor["id"])).fetchone()
    if row is None:
        return None
    if row["awaiting_reply"]:
        return "awaiting a reply since the last outreach — not sending again"
    if row["last_outreach_at"]:
        interval = timedelta(hours=profile["proactive_min_interval_hours"])
        last = datetime.fromisoformat(row["last_outreach_at"])
        if now - last < interval:
            return (f"rate cap: at most one unprompted outreach per "
                    f"{profile['proactive_min_interval_hours']}h")
    return None


def record_proactive_outreach(profile_id: str, interactor_id: str) -> None:
    conn = db.connect()
    conn.execute(
        "INSERT INTO proactive_state (profile_id, interactor_id,"
        " last_outreach_at, awaiting_reply) VALUES (?,?,?,1)"
        " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
        " last_outreach_at=excluded.last_outreach_at, awaiting_reply=1",
        (profile_id, interactor_id, db.utcnow()))
    conn.commit()


def clear_awaiting_reply(profile_id: str, interactor_id: str) -> None:
    """The recipient replied — lift the suppression so future outreach may
    resume (subject to the rate cap)."""
    conn = db.connect()
    conn.execute(
        "UPDATE proactive_state SET awaiting_reply=0"
        " WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id))
    conn.commit()


def relationship(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM relationships WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id),
    ).fetchone()
    return dict(row) if row else None


def profile_out(row: dict) -> ProfileOut:
    return ProfileOut(
        id=row["id"],
        owner_id=row["owner_id"],
        kind=row["kind"],
        display_name=row["display_name"],
        persona=row["persona"],
        demographics=json.loads(row["demographics"]),
        sources=json.loads(row["sources"]),
        anonymous=bool(row["anonymous"]),
        adult_mode=bool(row["adult_mode"]),
        interaction_scope=row["interaction_scope"],
        moderation_mode=row["moderation_mode"],
        aging_enabled=bool(row["aging_enabled"]),
        base_age=row["base_age"],
        effective_age=persona.effective_age(row),
        successor_owner=row["successor_owner"],
        purpose=row["purpose"],
        maturity=row["maturity"],
        cloud_contribution=bool(row["cloud_contribution"]),
        status=row["status"],
        created_at=row["created_at"],
    )


def message_out(row: dict) -> MessageOut:
    # Unapproved profile content is never shown to interactors (PRD 6.5).
    visible = row["status"] == "approved" or row["role"] == "interactor"
    return MessageOut(
        id=row["id"],
        role=row["role"],
        content=row["content"] if visible else None,
        status=row["status"],
        flag_reason=row["flag_reason"],
        created_at=row["created_at"],
    )


def source_items(profile_id: str, pdi=None) -> list[dict]:
    """Source items with content resolved from the PDI vault if sealed."""
    rows = db.connect().execute(
        "SELECT * FROM source_items WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC", (profile_id,),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        if item["pdi_key"] and pdi is not None:
            raw = pdi.get(item["pdi_key"])
            item["content"] = json.loads(raw)["content"] if raw else None
        out.append(item)
    return out


def biometric_domain(biometrics: dict) -> str | None:
    """Claim 24: map monitoring signals to the specialist domain they call for."""
    condition = (biometrics.get("condition") or "").lower()
    if condition in ("anxiety", "depression", "stress", "phobia"):
        return "mental_health"
    if condition in ("physical_distress", "physical_injury"):
        return "medical"
    if condition == "financial_stress":
        return "finance"
    try:
        if float(biometrics.get("stress_level") or 0) >= 0.7:
            return "mental_health"
    except (TypeError, ValueError):
        pass
    return None


def biometrics_recovered(biometrics: dict | None) -> bool:
    """Whether a fresh biometric reading indicates the episode has passed —
    the signal to hand a conversation back from a specialist to the primary
    profile. Recovery requires *positive* evidence: a reading that carries no
    concerning domain and a low stress level. Absent biometrics are not
    recovery (the specialist stays engaged until monitoring says otherwise)."""
    if not biometrics:
        return False
    if biometric_domain(biometrics) is not None:
        return False
    try:
        return float(biometrics.get("stress_level") or 0) < 0.4
    except (TypeError, ValueError):
        return False
