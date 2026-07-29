# Invention Disclosure — QRME

*Inventor: David Bianchi. Recorded 2026-07-29. This document, together
with this repository's commit history and tagged releases, is a dated
public record of conception and reduction to practice. It is written to
be handed to a patent attorney as the starting point for provisional
applications. It is a factual record, not legal advice and not a license
(see LICENSE).*

## 1. Owner-governed synthetic profile as a product

**The process:** a person's likeness, voice, knowledge and manner are
compiled into an interactive synthetic profile that the owner governs as
property: per-relationship steering, owner moderation queues, watermarked
outputs, licensing and revenue surfaces, erasure on demand. Every
approved textual render is stamped with the producing profile's
credential so provenance survives the reply leaving the platform
(`qrme/watermark.py`).

## 2. Membership gating as a single application-wide chokepoint

**The process:** paid-capability gating implemented as one FastAPI
application dependency over a capability table, rather than per-route
checks — a capability cannot be added to the product and forgotten at a
route, because no route opts in (`qrme/tiers.py`, `qrme/api.py`).
Escalation-adjacent paths are structurally excluded from gating
(`NEVER_GATED`).

## 3. Request-scoped bring-your-own-credential inference

**The process:** a caller's model API key rides one request in a header
into a context variable read by the provider layer; generations run on
the caller's credential, which is never persisted and never logged, while
requests without one use the deployment's key — the operator "lending"
theirs (`qrme/llm.py`, `qrme/api.py` middleware; shipped v0.4.3 line).

## 4. Vault-sealed tandem exchanges with auditable custody

**The process:** sensitive exchanges between a user's guardian (JIM-mini)
and a profile specialist are sealed into an encrypted personal-data vault
(PDI) at the seal point, with a custody viewer exposing the audit chain
and full provenance trail per record, scoped strictly to the user's own
records (shipped v0.3.x line).

## 5. Desk beacons and lend-a-microphone

**The process:** a live workspace published as a scannable physical
QR sticker (desk beacons), and a profile-to-profile microphone lending
flow with named handover and per-channel gain (shipped v0.2.2 and
v0.4.0 lines respectively).

## 6. Weighted hybrid personas with a public composition

**The process:** one synthetic profile blended from several source
profiles with normalized weights and named borrowed aspects; the blend
recorded per-constituent and published to any reader; the persona's
prompt carries an honesty rule (never claims to be any single
constituent). Departed sources are permitted by design; rated sources
and free-hand `kind=hybrid` are structurally refused
(`qrme/composite.py`; shipped v0.12.0, recorded 2026-07-29).

## 7. Predictive simulation with evidence-earned confidence

**The process:** a real-time simulation of the represented person's
decisions and workflow whose confidence score is computed from the
volume of real conditioning evidence (source items, remembered turns,
latent embedding) rather than from model output; the narrative is
watermarked synthetic and structurally excluded from distribution
(`qrme/simulation.py`; shipped v0.12.0).

## 8. Environmental context beside biometric context

**The process:** interaction requests carry an environment payload
(location, conditions, local time, activity) stored beside real-time
biometric context and rendered into inference conditioning, so replies
adapt to where the person actually is (`environment_context`; shipped
v0.12.0).

## 9. Proceeds designations with token-lifecycle succession

**The process:** crowdfunding proceeds routed in advance to named
designees whose shares must sum to exactly 100; campaigns refused until
a designation exists; each donation split at the door onto an auditable
ledger in integer cents; and control passing at verified owner death by
revoking the old credential and minting one for the chosen successor —
"leave it in good hands" enforced by token lifecycle rather than status
checks (`qrme/campaigns.py`; shipped v0.13.0).

## 10. Departmental agent coordination over revocable scopes

**The process:** an organization staffs departments with role-specific
synthetic agents whose data pulls are scoped by independently revocable
grants; one goal fans out across departments, each agent contributing
from its own scoped material, the initiating agent composing the joint
plan; the record sealed into an encrypted vault when the tandem is
configured (`qrme/organization.py`; shipped v0.13.0).

---

*Attorney notes: repository first became public before this disclosure;
for jurisdictions with grace periods, the earliest public commit and the
earliest tagged release containing each mechanism are the operative
dates.*
