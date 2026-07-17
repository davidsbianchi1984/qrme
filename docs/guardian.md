# JIM-mini / Guardian — the personal guidance tandem layer

Guardian is the monitoring half of a **tandem architecture**. Two systems run
together:

- **QRME — Synthetic User Profile Management** (patent app 19/056,418): builds
  and maintains relationship-aware, engagement-adaptive AI profiles.
- **JIM-mini / Guardian — Networked Responsive Personal Guidance System for
  Known Conditions** (patent app 19/038,196): an always-on monitor that watches
  a user's biometric and contextual signals, detects known conditions, and
  triggers help.

The value of running them together: instead of answering a struggling user
with a generic model, Guardian **pulls the appropriate specialized synthetic
agent from QRME** and delivers guidance through it — a closed-loop, proactive
platform. This mirrors QRME amended claim 6 (biometric monitoring data adapts
the profile interaction).

## The closed loop

```
 wearable / app sample ─▶ Guardian.monitor()
                              │
                              ▼
                       conditions.detect()        ── known-condition rules
                              │  (condition, severity)
              ┌───────────────┼────────────────────────────┐
              ▼               ▼                             ▼
       log biometric    trigger specialist            if critical:
                         = a QRME profile                escalate to
                         registered for the              emergency contact
                         condition                       / live person
                              │
                              ▼
                 persona-conditioned reply
                 → moderated → remembered
```

Examples of condition → specialist routing (PRD / patent):

| Detected condition | Specialist agent (a QRME profile) |
|---|---|
| panic attack / acute anxiety | Anxiety Specialist |
| financial crisis | Crypto / Trading Strategy |
| relationship distress | Relationship Advisor |
| low blood oxygen | First-aid / physical-distress guide |

## Detection signals (`qrme/conditions.py`)

A transparent rule layer over a biometric sample plus optional free text:

- **Biometric**: heart rate vs. the user's resting baseline, respiratory rate,
  blood oxygen (SpO₂).
- **Context**: free-text cues per condition domain, and crisis language that
  forces immediate escalation.

Each detection carries a `severity`: `info` (log only), `guidance` (trigger the
specialist), or `critical` (trigger **and** escalate).

## API

| Endpoint | Purpose |
|---|---|
| `POST /guardian/enroll/{interactor_id}` | Enroll a user: terms/guardian consent, emergency contact (+ consent to contact), device pairing, resting-HR baseline, goals |
| `POST /guardian/specialists` | Register a QRME profile as the specialist for a condition |
| `POST /guardian/monitor/{interactor_id}` | Ingest one biometric/context sample; runs the full loop and returns detection + guidance + any escalation |
| `GET /guardian/events/{interactor_id}` | The full event timeline (biometric → detection → guidance → escalation → resolved) |

## Privacy & safety

- **Enrollment gates**: terms consent required; minors require guardian consent.
- **Consent to contact**: an emergency contact is only notified when the user
  consented (`contact_consent`) and provided a number.
- **Moderation**: specialist guidance passes the same outbound moderation
  pipeline as any QRME reply before it is delivered.
- **Memory**: guidance episodes are written to the specialist profile's
  per-user memory, so the agent remembers the episode across sessions — and the
  user can view/clear it through the existing memory endpoints.

## Out of scope for v1

Live device streaming/pairing protocols, real emergency-services dispatch, and
the specialist "knowledge pack" marketplace are represented structurally
(enrollment flags, specialist registry, event log) but not implemented as live
integrations.
