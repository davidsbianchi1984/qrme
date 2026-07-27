"""Is this profile a real person, and are they who they say they are?

Two different questions, and a badge that runs them together is worse than no
badge at all.

* **Is there a real person behind it** — answered by ``kind``. A ``fictional``
  profile depicts nobody; ``self`` and ``other_person`` depict somebody.
* **Has anyone checked they are who they claim** — answered here, and the
  honest answer is usually *not much*.

The ladder is :data:`qrme.signatures.PROOFING_LEVELS`, reused rather than
reinvented so the platform has one meaning for "how well is this identity
established" instead of two that drift:

``self_asserted`` → ``federated`` → ``document`` → ``in_person``

The rule that makes the badge worth anything is the one ``signatures.enroll``
already applies: **anything above self-asserted needs a named attestor.** Who
checked is part of the record, not a footnote. A "verified" badge with nobody
behind it is a credential the platform minted for itself, and this codebase
spends most of its design arguing against exactly that.

So a profile can say **verified** and still be honest about how thin the check
is, because :func:`status` always returns the level alongside the badge and the
surfaces render both. What it must never do is show the word on its own.
"""

from __future__ import annotations

from . import db
from .signatures import PROOFING_LEVELS, _level_rank

# What each rung actually means, in the words a person reading a profile needs
# rather than the words an identity engineer would use.
MEANING: dict[str, str] = {
    "self_asserted": "they say so, and nobody has checked",
    "federated": "confirmed through another account they control",
    "document": "an identity document was checked",
    "in_person": "somebody met them and checked in person",
}


class VerificationError(ValueError):
    """A verification record that cannot stand up."""


def verify(profile_id: str, level: str, attestor: str | None = None,
           method: str | None = None, ref: str | None = None) -> dict:
    """Record how well this profile's identity has been established.

    ``ref`` points at evidence held elsewhere. Never store the identity
    document itself — the same rule ``signatures.enroll`` follows, for the same
    reason.
    """
    if level not in PROOFING_LEVELS:
        raise VerificationError(
            f"unknown proofing level {level!r}; expected one of "
            f"{', '.join(PROOFING_LEVELS)}")
    if _level_rank(level) > 0 and not attestor:
        raise VerificationError(
            f"proofing level {level!r} requires an attestor — who checked the "
            "identity is part of the record, not a footnote")

    conn = db.connect()
    conn.execute(
        "INSERT INTO profile_verification (profile_id, level, attestor,"
        " method, ref, checked_at) VALUES (?,?,?,?,?,?)"
        " ON CONFLICT (profile_id) DO UPDATE SET level=excluded.level,"
        " attestor=excluded.attestor, method=excluded.method,"
        " ref=excluded.ref, checked_at=excluded.checked_at",
        (profile_id, level, attestor, method, ref, db.utcnow()))
    conn.commit()
    return status(profile_id)


def status(profile_id: str) -> dict:
    """The badge, and everything needed to read it honestly.

    ``verified`` is True for any recorded level, including ``self_asserted`` —
    the badge says *a real person stands behind this and this is who they say
    they are*. ``level`` and ``means`` say how far anyone went to check, and no
    surface should show the first without the second.
    """
    row = db.connect().execute(
        "SELECT p.kind, v.level, v.attestor, v.method, v.checked_at"
        "  FROM profiles p"
        "  LEFT JOIN profile_verification v ON v.profile_id = p.id"
        " WHERE p.id=?", (profile_id,)).fetchone()
    return _read(row)


def statuses(profile_ids: list[str]) -> dict[str, dict]:
    """The same badge for many profiles, in one query.

    A friends list needs one of these per row, and fetching them one at a time
    made a list of fifty into fifty round trips. The formatting stays in
    :func:`_read` so both paths cannot drift apart — which is the usual cost of
    adding a batch version beside a single one.
    """
    if not profile_ids:
        return {}
    marks = ",".join("?" * len(profile_ids))
    rows = db.connect().execute(
        "SELECT p.id, p.kind, v.level, v.attestor, v.method, v.checked_at"
        "  FROM profiles p"
        "  LEFT JOIN profile_verification v ON v.profile_id = p.id"
        f" WHERE p.id IN ({marks})", list(profile_ids)).fetchall()
    return {r["id"]: _read(r) for r in rows}


def _read(row) -> dict:
    if row is None:
        return {}
    if row["kind"] == "fictional":
        return {"verified": False, "real_person": False,
                "note": "an invented person — there is nobody to verify"}
    if row["level"] is None:
        return {"verified": False, "real_person": True,
                "note": "depicts a real person; no identity check recorded"}
    return {
        "verified": True,
        "real_person": True,
        "level": row["level"],
        "rank": _level_rank(row["level"]),
        "means": MEANING[row["level"]],
        "attestor": row["attestor"],
        "method": row["method"],
        "checked_at": row["checked_at"],
        # The honest caveat, carried with the badge rather than left to a
        # reader to work out. Self-asserted is the bottom rung and saying so
        # beside the word is the difference between a badge and a claim.
        "caveat": (None if _level_rank(row["level"]) > 0 else
                   "self-asserted: the badge confirms a real person stands "
                   "behind this profile, not that a document was checked"),
    }
