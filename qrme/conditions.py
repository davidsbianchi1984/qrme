"""Known-condition detection for the JIM-mini / Guardian layer.

Guardian is the always-on monitor of the tandem architecture (patent app
19/038,196): it watches a user's biometric and contextual signals and, when a
known condition appears, names the condition and a severity so the Guardian
orchestrator can pull the matching specialist agent from QRME and, if needed,
escalate to a live person or emergency contact.

Detection here is a transparent rule layer over a biometric sample plus
optional free text. It maps signals to a ``condition`` (a domain key that a
specialist profile is registered against) and a ``severity``:

- ``info``     — noticed, no action beyond logging
- ``guidance`` — trigger the specialist agent
- ``critical`` — trigger the specialist AND escalate immediately
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Condition domain keys — a specialist profile is registered against one of these.
ANXIETY = "anxiety"
DEPRESSION = "depression"
FINANCIAL_STRESS = "financial_stress"
RELATIONSHIP = "relationship"
PHYSICAL_DISTRESS = "physical_distress"


@dataclass
class Detection:
    condition: str
    severity: str            # info | guidance | critical
    reason: str
    signals: dict = field(default_factory=dict)


# Free-text cues per condition (case-insensitive whole-word/phrase match).
_TEXT_CUES: list[tuple[str, list[str]]] = [
    (ANXIETY, ["panic", "panic attack", "anxious", "anxiety", "can't breathe",
               "racing thoughts", "overwhelmed"]),
    (DEPRESSION, ["hopeless", "worthless", "empty", "no point", "can't get out of bed"]),
    (FINANCIAL_STRESS, ["broke", "debt", "bankrupt", "can't pay", "financial crisis",
                        "lost my job", "rent", "eviction"]),
    (RELATIONSHIP, ["breakup", "broke up", "divorce", "fight with", "lonely",
                    "my partner", "my ex"]),
]

# Crisis phrases force immediate escalation regardless of biometrics.
_CRISIS = re.compile(
    r"\b(kill myself|end it all|suicide|hurt myself|don't want to live)\b", re.I
)


def detect(sample: dict, text: str | None = None) -> Detection | None:
    """Return the highest-severity detection for a sample, or None.

    ``sample`` may include: heart_rate (bpm), resting_heart_rate (bpm),
    respiratory_rate (breaths/min), blood_oxygen (SpO2 %), and a free-text
    note supplied separately as ``text``.
    """
    note = (text or sample.get("note") or "").strip()

    if note and _CRISIS.search(note):
        return Detection(
            ANXIETY, "critical",
            "crisis language detected — immediate escalation",
            {"text": note},
        )

    spo2 = sample.get("blood_oxygen")
    if spo2 is not None and spo2 < 90:
        return Detection(
            PHYSICAL_DISTRESS,
            "critical" if spo2 < 88 else "guidance",
            f"low blood oxygen (SpO2 {spo2}%)",
            {"blood_oxygen": spo2},
        )

    # Elevated heart + respiratory rate relative to the user's baseline reads
    # as acute anxiety / panic — the canonical Guardian trigger.
    hr = sample.get("heart_rate")
    resting = sample.get("resting_heart_rate", 70)
    rr = sample.get("respiratory_rate")
    if hr is not None and hr >= resting + 40 and (rr is None or rr >= 20):
        severity = "critical" if hr >= resting + 70 else "guidance"
        return Detection(
            ANXIETY, severity,
            f"heart rate {hr} bpm ({hr - resting} over resting)"
            + (f", respiratory rate {rr}/min" if rr else ""),
            {"heart_rate": hr, "resting_heart_rate": resting, "respiratory_rate": rr},
        )

    if note:
        for condition, cues in _TEXT_CUES:
            for cue in cues:
                if re.search(rf"\b{re.escape(cue)}\b", note, re.I):
                    return Detection(
                        condition, "guidance",
                        f"reported concern matching '{cue}'",
                        {"text": note},
                    )

    return None
