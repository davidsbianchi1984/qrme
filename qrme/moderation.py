"""Outbound content moderation pipeline (PRD 6.5 / 9).

Every profile-generated message passes through here before it becomes
visible to anyone. v1 is a rule-based checker: relationship boundaries,
age-appropriateness for minors, and a small deny-pattern list. The verdict
combines with the profile's moderation mode: ``manual`` holds everything for
owner approval; ``auto`` publishes unless flagged.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime

_DENY_PATTERNS = [
    (re.compile(r"\b(ssn|social security number)\b", re.I), "possible sensitive data"),
    (re.compile(r"\bkill yourself\b", re.I), "harmful content"),
    (re.compile(r"\b(credit card number|cvv)\b", re.I), "possible financial data"),
]

_ADULT_PATTERNS = [
    (re.compile(r"\b(explicit|nsfw)\b", re.I), "age-inappropriate for minor"),
]


@dataclass
class Verdict:
    approved: bool
    reason: str | None = None


def _age_of(birthdate: str | None) -> int | None:
    if not birthdate:
        return None
    born = date.fromisoformat(birthdate)
    today = datetime.now().date()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def review(content: str, relationship: dict | None, interactor: dict,
           maturity: str = "balanced") -> Verdict:
    """``maturity`` is the profile's filter dial (strict | balanced | open).
    Minors are always held to strict, whatever the profile is set to."""
    for pattern, reason in _DENY_PATTERNS:
        if pattern.search(content):
            return Verdict(False, reason)

    age = _age_of(interactor.get("birthdate"))
    strict = maturity == "strict" or (age is not None and age < 18)
    if strict:
        for pattern, reason in _ADULT_PATTERNS:
            if pattern.search(content):
                reason = (reason if (age is not None and age < 18)
                          else "blocked by strict maturity filter")
                return Verdict(False, reason)

    if relationship:
        for topic in json.loads(relationship["boundaries"]):
            if re.search(rf"\b{re.escape(topic)}\b", content, re.I):
                return Verdict(False, f"restricted topic for this relationship: {topic}")

    return Verdict(True)
