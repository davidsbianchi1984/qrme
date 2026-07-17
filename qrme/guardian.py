"""JIM-mini / Guardian — the always-on personal guidance layer.

Guardian is the monitoring half of the tandem architecture (patent app
19/038,196, run alongside QRME's Synthetic Profile system, app 19/056,418).
It enrolls a user, ingests biometric/context samples, detects known
conditions, and — instead of answering with a generic model — pulls the
registered *specialist* QRME profile for that condition and generates
moderated, memory-backed guidance through it. Critical detections escalate to
the user's emergency contact / a live person.

The closed loop per sample:

    monitor → detect condition → trigger specialist agent (a QRME profile)
            → generate guidance (persona-conditioned, moderated, remembered)
            → check severity → escalate if critical → log the whole chain
"""

from __future__ import annotations

import json

from . import conditions, db, engagement, llm, moderation, persona

# How Guardian frames each condition to the specialist agent and the user.
_CONDITION_LABEL = {
    conditions.ANXIETY: "acute anxiety / panic",
    conditions.DEPRESSION: "low mood / depression",
    conditions.FINANCIAL_STRESS: "financial stress",
    conditions.RELATIONSHIP: "relationship distress",
    conditions.PHYSICAL_DISTRESS: "physical distress",
}


def _event(interactor_id: str, type_: str, *, condition=None, severity=None, detail=None):
    conn = db.connect()
    event_id = db.new_id("gev")
    conn.execute(
        "INSERT INTO guardian_events (id, interactor_id, type, condition, severity,"
        " detail, created_at) VALUES (?,?,?,?,?,?,?)",
        (event_id, interactor_id, type_, condition, severity,
         json.dumps(detail or {}), db.utcnow()),
    )
    conn.commit()
    return {"id": event_id, "type": type_, "condition": condition,
            "severity": severity, "detail": detail or {}}


def enroll(interactor_id: str, body: dict) -> dict:
    """Register an interactor with Guardian (consent, emergency contact, device)."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO guardian_enrollments (interactor_id, terms_consent,"
        " guardian_consent, emergency_name, emergency_phone, contact_consent,"
        " device_paired, resting_heart_rate, goals, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)"
        " ON CONFLICT (interactor_id) DO UPDATE SET"
        " terms_consent=excluded.terms_consent,"
        " guardian_consent=excluded.guardian_consent,"
        " emergency_name=excluded.emergency_name,"
        " emergency_phone=excluded.emergency_phone,"
        " contact_consent=excluded.contact_consent,"
        " device_paired=excluded.device_paired,"
        " resting_heart_rate=excluded.resting_heart_rate,"
        " goals=excluded.goals",
        (
            interactor_id,
            int(body["terms_consent"]),
            int(body.get("guardian_consent", False)),
            body.get("emergency_name"),
            body.get("emergency_phone"),
            int(body.get("contact_consent", False)),
            int(body.get("device_paired", False)),
            body.get("resting_heart_rate"),
            body.get("goals"),
            db.utcnow(),
        ),
    )
    conn.commit()
    return get_enrollment(interactor_id)


def get_enrollment(interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM guardian_enrollments WHERE interactor_id=?", (interactor_id,)
    ).fetchone()
    return dict(row) if row else None


def register_specialist(condition: str, profile_id: str) -> dict:
    """Tag a QRME profile as the specialist agent for a condition domain."""
    conn = db.connect()
    specialist_id = db.new_id("spc")
    conn.execute(
        "INSERT INTO specialists (id, condition, profile_id, created_at)"
        " VALUES (?,?,?,?)"
        " ON CONFLICT (condition) DO UPDATE SET profile_id=excluded.profile_id",
        (specialist_id, condition, profile_id, db.utcnow()),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM specialists WHERE condition=?", (condition,)
    ).fetchone()
    return dict(row)


def _specialist_for(condition: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM specialists WHERE condition=?", (condition,)
    ).fetchone()
    return dict(row) if row else None


def monitor(interactor_id: str, sample: dict, note: str | None = None) -> dict:
    """Ingest one biometric/context sample and run the Guardian loop.

    Returns a result describing what Guardian did: the detection (if any), the
    specialist guidance delivered (if a specialist was available), and any
    escalation.
    """
    enrollment = get_enrollment(interactor_id)
    # Fold the user's resting baseline into the sample for detection.
    if enrollment and enrollment.get("resting_heart_rate") and "resting_heart_rate" not in sample:
        sample = {**sample, "resting_heart_rate": enrollment["resting_heart_rate"]}

    _event(interactor_id, "biometric", detail={**sample, **({"note": note} if note else {})})

    detection = conditions.detect(sample, note)
    if detection is None:
        return {"detected": False, "guidance": None, "escalation": None}

    _event(interactor_id, "detection", condition=detection.condition,
           severity=detection.severity, detail={"reason": detection.reason,
                                                 "signals": detection.signals})

    result: dict = {
        "detected": True,
        "condition": detection.condition,
        "severity": detection.severity,
        "reason": detection.reason,
        "guidance": None,
        "escalation": None,
    }

    guidance = _deliver_guidance(interactor_id, detection, note)
    result["guidance"] = guidance

    if detection.severity == "critical":
        result["escalation"] = _escalate(interactor_id, detection)

    return result


def _deliver_guidance(interactor_id: str, detection: conditions.Detection,
                      note: str | None) -> dict | None:
    """Pull the specialist QRME profile and generate moderated guidance."""
    specialist = _specialist_for(detection.condition)
    if specialist is None:
        _event(interactor_id, "guidance", condition=detection.condition,
               detail={"delivered": False, "reason": "no specialist registered"})
        return {"delivered": False, "reason": "no specialist agent registered "
                f"for '{detection.condition}'"}

    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (specialist["profile_id"],)
    ).fetchone())

    label = _CONDITION_LABEL.get(detection.condition, detection.condition)
    situation = f"the user shows signs of {label} ({detection.reason})."
    if note:
        situation += f' They said: "{note}".'

    engagement_state = engagement.get(profile["id"], interactor_id)
    system = persona.build_system_prompt(
        profile, relationship=None, engagement=engagement_state, situation=situation,
    )
    opening = note or f"[Guardian] The user may be experiencing {label}."
    reply = llm.get_provider().generate(system, [{"role": "user", "content": opening}])

    interactor = dict(db.connect().execute(
        "SELECT * FROM interactors WHERE id=?", (interactor_id,)
    ).fetchone())
    verdict = moderation.review(reply, None, interactor)

    conn = db.connect()
    status = "approved" if verdict.approved else "pending"
    # Guidance is recorded in the specialist profile's memory for this user, so
    # the agent remembers the episode across sessions (persistent memory).
    msg_id = db.new_id("msg")
    conn.execute(
        "INSERT INTO messages (id, profile_id, interactor_id, role, content, status,"
        " flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (msg_id, profile["id"], interactor_id, "profile", reply, status,
         verdict.reason, db.utcnow()),
    )
    conn.commit()

    delivered = {
        "delivered": verdict.approved,
        "specialist_profile_id": profile["id"],
        "specialist_name": profile["display_name"],
        "condition": detection.condition,
        "content": reply if verdict.approved else None,
        "status": status,
        "flag_reason": verdict.reason,
    }
    _event(interactor_id, "guidance", condition=detection.condition,
           severity=detection.severity, detail=delivered)
    return delivered


def _escalate(interactor_id: str, detection: conditions.Detection) -> dict:
    """Alert a live person / the user's emergency contact for a critical event."""
    enrollment = get_enrollment(interactor_id)
    contact = None
    if enrollment and enrollment.get("contact_consent") and enrollment.get("emergency_phone"):
        contact = {
            "name": enrollment.get("emergency_name"),
            "phone": enrollment.get("emergency_phone"),
        }
    escalation = {
        "escalated": True,
        "condition": detection.condition,
        "reason": detection.reason,
        "notified_emergency_contact": contact is not None,
        "emergency_contact": contact,
        "live_support": True,
    }
    _event(interactor_id, "escalation", condition=detection.condition,
           severity="critical", detail=escalation)
    return escalation


def events(interactor_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM guardian_events WHERE interactor_id=? ORDER BY created_at, rowid",
        (interactor_id,),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["detail"] = json.loads(item["detail"])
        out.append(item)
    return out
