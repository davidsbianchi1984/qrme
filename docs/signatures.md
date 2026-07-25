# Signatures: the same Face ID gesture, a signature that survives dispute

**Status: implemented** in `qrme/signatures.py`, `qrme/webauthn.py` and
`qrme/routers/signatures.py`, with the endpoint surface of §9 live. The
native clients do not drive it yet. This document remains the reasoning:
why each part exists, and — as loudly — what it does not prove.

The starting instinct was right: *a real Face ID should be enough.* The user
gesture in this design is exactly that. What changes is what comes back from
it.

---

## 1. Why the obvious version fails

The naive implementation is four lines:

```swift
LAContext().evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                           localizedReason: "Sign the handoff") { ok, _ in
    if ok { api.post("/handoff/sign", ["signed": true]) }   // ← the whole problem
}
```

That returns a **boolean, to the app**. Everything after it is the app's word.
A patched client, a rooted device, or anyone who can craft an HTTP request
sends `{"signed": true}` and the server cannot tell the difference. In a
dispute the record says "our software says he agreed," which is precisely the
claim under dispute.

Face ID is not the weak part. It is a good sensor with a good enclave. The
weak part is that `evaluatePolicy` produces **no artifact** — nothing exists
afterwards that a third party could check.

## 2. What replaces it

**WebAuthn / passkeys.** Same prompt, same face, same half-second. But the
private key lives in the Secure Enclave (or StrongBox, or TPM), the app never
sees it, and what comes back is a **signature over a server-issued challenge**
that anyone holding the public key can verify — years later, on a different
machine, without trusting our software at all.

| | `evaluatePolicy` | WebAuthn assertion |
| --- | --- | --- |
| User experience | Face ID prompt | Face ID prompt |
| Returned to app | `Bool` | signature + signed data |
| Forgeable by a modified client | Yes | No |
| Verifiable by a third party | No | Yes |
| Survives "I never agreed to that" | No | Yes |

Three things have to be true for that signature to mean anything. Each gets a
section.

## 3. Enrollment: make the key stand for a person

A passkey proves *this credential was used*. It says nothing about **who** used
it unless enrollment established that. A key enrolled by an anonymous signup is
a very strong signature by an unknown party.

So enrollment is a one-time identity-proofing step, and its result is recorded
next to the credential:

| Level | How identity was established | Good for |
| --- | --- | --- |
| `self_asserted` | Email/phone control only | Nothing that will be disputed |
| `federated` | SSO from an employer/health-system IdP that proofed them | OSHA logs, internal handoffs |
| `document` | Government ID + liveness check, one time, at enrollment | Care handoffs, BAAs, licensing |
| `in_person` | A human verified them against ID | Anything above |

Store: level, method, evidence reference, who attested, when. **Not** the ID
image itself and **never** a face template — the biometric never leaves the
user's device in this design, and it must not start being collected here.
Enrollment proofing is checked against a per-document-type minimum before a
signature is accepted, so a `self_asserted` credential simply cannot sign a
care handoff.

A credential enrolled below the required level is not upgraded silently. The
user re-proofs and the new level applies from that moment forward, never
retroactively.

## 4. Sign the document, not "yes"

This is the part most implementations skip, and it is what turns
authentication into a signature.

In sign-in, the challenge is a random nonce. Here it is **the document**:

```
challenge = SHA-256( canonical_json({
    "v": 1,
    "envelope": envelope_id,
    "doc_sha256": <hash of the exact bytes being signed>,
    "meaning": "I attest this medication handoff is accurate and complete",
    "signer": <account id>,
    "credential": <credential id>,
    "issued_at": <RFC 3339, server clock>,
    "expires_at": <issued_at + 120s>,
    "rp": "qrme.app"
}) )
```

The authenticator signs over `authenticatorData || SHA-256(clientDataJSON)`,
and `clientDataJSON` contains that challenge. So the resulting signature binds,
inseparably: this credential + user verification actually happened + **this
exact document** + this stated meaning + this moment. Change one byte of the
document and the signature stops verifying.

`meaning` is not decoration. ESIGN and Part 11 both want the *purpose* of the
signature on the record — approval, authorship, review, responsibility — and
it belongs inside the signed bytes rather than in a column beside them.

Options that matter at request time:

- `userVerification: "required"` — this is what makes the biometric mandatory
  rather than a mere presence tap. Without it the user can dismiss with a
  button press and the assertion still verifies.
- `attestation: "direct"` at enrollment, so the **AAGUID** is captured and the
  evidence can say which authenticator model was used.
- One challenge, one document, one use. Short expiry. Server-side single-use
  enforcement, not client-side.

## 5. What the user saw is what they signed

Here is the honest limit, stated where nobody can miss it.

**WebAuthn has no trusted display.** The OS prompt says *"Sign in to
qrme.app"* — it does not and cannot say *"you are transferring care of Marisol
Reyes, 4mg, 22:00."* The `txAuthSimple` extension that would have shown
transaction text was removed from the specification and never shipped broadly.
So the guarantee is: *the holder of this credential performed user verification
against this hash.* The link from that hash to **what appeared on the screen**
is our software's job.

We can make that link strong, and we should stop short of calling it
cryptographic:

1. The document is rendered to a fixed, versioned presentation — same input,
   same pixels — and `doc_sha256` covers **the rendered form**, not just the
   underlying data.
2. The exact text shown is stored verbatim in the evidence package, so a
   dispute reproduces the screen rather than arguing about it.
3. The confirmation screen is the last thing before the prompt, with no
   intervening navigation, and the app records the interval.
4. For the highest tier, the confirmation happens on a **different device**
   than the one presenting the document (§7) — a screen the presenting
   application cannot paint.

Anyone claiming WYSIWYS from WebAuthn alone is overselling it. Write it down as
a residual risk in the design record and treat item 4 as the mitigation.

## 6. The evidence package

What gets sealed the moment a signature verifies. This is the artifact a
dispute is fought over, so it is stored whole and never regenerated:

- `credential_id`, `aaguid`, and **the public key itself** — copied here, not
  looked up. A passkey the user later deletes must not take the ability to
  verify their past signatures with it.
- `signature`, `authenticator_data`, `client_data_json` — raw, exactly as
  received.
- `up` / `uv` flags, and **`be` / `bs`** (backup-eligible / backed-up) — see
  below.
- `sign_count`, and whether it moved backwards.
- The canonical payload from §4 and the rendered text from §5.
- Enrollment record reference and proofing level at time of signing.
- Server timestamp; and for the top tier an **RFC 3161 trusted timestamp**,
  because our own clock is our own assertion.
- The verifier's own result and library version at seal time.

Sealed into PDI as an ordinary tenant record and chained into the
tamper-evident audit log, so the *existence and order* of signatures is
protected by something other than the row they live in.

### The `be`/`bs` flags deserve their own paragraph

Modern passkeys **sync**. iCloud Keychain and Google Password Manager replicate
the credential across every device in that account, which is wonderful for
sign-in and a real weakening for non-repudiation: "my key" becomes "a key
present on an unknown number of devices behind a cloud password."

Do not pretend otherwise. Record `be`/`bs` in the evidence so a dispute can see
whether the credential was syncable at signing time, and for the highest tier
require a **device-bound** credential (`be = 0`) — a platform authenticator
that refuses to sync, or a hardware security key. That is a deliberate
usability cost, taken only where the record justifies it.

## 7. AR and VR: glasses, goggles, headsets

The same design, and the honest news is that the good case is already good.

**Apple Vision Pro — works today, unchanged.** visionOS exposes **Optic ID** as
a platform authenticator. `userVerification: "required"` is satisfied by an
iris scan, the key is in the Secure Enclave, and the assertion is
indistinguishable in structure from the Face ID one. Nothing product-specific
is needed: the same enrollment, the same challenge, the same evidence package.
Iris instead of face, and the biometric never leaves the device — same as Face
ID.

**Headsets without a platform authenticator — use hybrid transport.** Quest and
most Android XR devices do not expose headset biometrics to WebAuthn. The
answer is **cross-device authentication** (CDA, the "hybrid" transport): the
headset displays a QR code, the user's phone scans it, Face ID happens *on the
phone*, and the assertion travels back over an encrypted BLE-proximity tunnel.
The phone must be physically near the headset — that proximity check is part
of the protocol, not a convention.

This is the fallback, and it is also the *strongest* option, because of §5: the
confirmation renders on the phone's own screen, which the immersive application
cannot draw over.

**Smart glasses with no display of their own** proxy to the paired phone. Same
path.

### Why WYSIWYS is harder in XR, and what to do

In a headset, the application renders **everything the user can see**. There is
no window chrome, no address bar, no OS-level boundary the user can point to
and say "that part wasn't the app." A malicious or buggy immersive scene can
present one document and be signing another, and the user has no independent
surface to check against.

So, for XR:

- On a headset with **no platform authenticator** (Quest, Android XR, anything
  unrecognised), the high tier **requires the hybrid path**, with the document
  re-rendered and confirmed on the phone. The headset is where you read; the
  phone is where you sign. This costs nothing, because those devices were
  going to need the phone anyway.
- **Vision Pro is not in that set.** Optic ID is a platform authenticator and
  its prompt is composited by the system, not by the app — exactly the position
  an iPhone is in with Face ID, and we do not send iPhones to a second device.
  The document is app-rendered in both cases, so requiring hybrid on visionOS
  would be a real usability cost buying no actual improvement. It signs
  on-device at every tier.
- Record `transport` (`internal` / `hybrid`) and the platform in the evidence.
  "Signed inside a headset" is a fact a dispute should be able to see.
- Do not accept an immersive-app screenshot as the rendering of record. The
  rendered text in §6 is authoritative.

There is also a privacy note worth putting in the product, not just the spec:
headset eye and face tracking are continuous and intimate, and passthrough
recording may capture bystanders. This design touches none of it — Optic ID
never releases a template — and that should be said plainly in the UI, because
users will reasonably assume the worst.

## 8. Which legal grade, and why not the stricter one

**Recommendation: ESIGN / UETA, built so that 21 CFR Part 11 is a
configuration change rather than a rewrite.**

ESIGN and UETA make an electronic signature enforceable when four things hold,
all of which this design produces as artifacts:

| Requirement | How it is met |
| --- | --- |
| Intent to sign | The `meaning` string, inside the signed bytes |
| Consent to transact electronically | Recorded at enrollment, versioned, withdrawable |
| Attribution to a person | Enrollment proofing (§3) + the assertion |
| Retention & accurate reproduction | The evidence package (§6), sealed and chained |

**Part 11 is a poor fit here, and adopting it by reflex would be a mistake.**
It governs records submitted to or kept for the **FDA** — clinical trials,
regulated manufacturing, device history. HIPAA does not require it; that is a
common and expensive confusion. JIM-mini's own terms state the product is a
wellness tool and **not a medical device**, so there is no FDA-regulated record
for Part 11 to attach to. Claiming Part 11 compliance without the validation
package, the SOPs, and the periodic re-validation behind it would be a worse
position than not claiming it.

What Part 11 would add, if a customer's use ever brings them in scope:

- Two distinct identification components at the first signing of a session
  (the passkey plus a second factor) — an options change, not an architecture
  change.
- A **signature manifestation** printed with the record: printed name, date and
  time, and meaning. §9 specifies this endpoint; build it now regardless,
  because it is also what makes a signature legible to a human being.
- Documented validation, change control, and record-retention SOPs. This is the
  expensive part and it is organisational, not technical.

**OSHA** recording (300/301 logs, training and certification records) is
satisfied comfortably by the ESIGN/UETA tier: it wants the certifier
identified and dated, which the evidence package exceeds.

**Do not** describe any of this as a "qualified electronic signature." That is
an eIDAS term of art requiring a qualified trust service provider and a
qualified signature creation device. This is not that, and it does not need to
be.

## 9. API surface

```
POST /signatures/enroll/options     → registration options (uv required,
                                       resident key, direct attestation)
POST /signatures/enroll             → verify attestation; store credential,
                                       AAGUID, be/bs, proofing level
GET  /signatures/credentials        → the caller's credentials + levels
DELETE /signatures/credentials/{id} → revoke forward; past signatures stay
                                       verifiable (public key is copied)

POST /signatures/request            → {document, meaning, tier} →
                                       {envelope_id, challenge, display_text,
                                        display_sha256, expires_at}
POST /signatures/sign               → verify assertion; seal evidence; chain
GET  /signatures/{id}               → evidence package + re-verification
GET  /signatures/{id}/certificate   → human-readable manifestation:
                                       printed name, date/time, meaning
POST /signatures/verify             → verify a package presented from outside
```

`/signatures/verify` matters: it lets a counterparty check a signature without
an account here, which is the difference between a record we vouch for and a
record that stands on its own.

### Tiers

| Tier | Proofing | Credential | Transport | Timestamp |
| --- | --- | --- | --- | --- |
| `basic` | `self_asserted` | any passkey | any | server clock |
| `standard` | `federated`+ | any passkey | any | server clock |
| `high` | `document`+ | device-bound (`be = 0`) | hybrid required in XR | RFC 3161 |

## 10. Where it binds in each product

Every one of these already exists as an unsigned or weakly-signed record. This
is not new surface area; it is evidence attached to decisions the products
already make.

**JIM-mini (Guardian)** — the medical cases that started this:
- Care and medication handoffs between caregivers — `high`.
- The autonomous-resuscitation waiver, which today is a signed-paper
  requirement in the terms — `high`, and never for a minor, unchanged.
- Guardian/parent enrollment for a child — `high`.
- Care-plan acknowledgement, incident and OSHA-style logs — `standard`.

**PDI** — custody decisions that are currently token-authorised:
- BAA execution (`POST /tenants/{id}/baa`) — `high`.
- Customer-key adoption and release — `high`. Releasing a key is irreversible
  for the records under it; that decision deserves a signature.
- Snapshot restore and tenant deletion — `high`.

**QRME**:
- Likeness releases for `kind="other_person"` — `high`. A real person granting
  their face is exactly the record that gets disputed later.
- Licensing grants and marketplace terms — `standard`.
- Terms clickwrap, currently a version + timestamp receipt — `standard`.
- Adult-tier attestation — `standard`, and it remains an age check rather than
  an identity broadcast.

## 11. What this does not prove

Written here so it is never inferred from silence:

- **Not that a specific human was present.** It proves the credential was used
  with user verification. A user who hands over an unlocked device, or enrolls
  a coerced second face, defeats it. Enrollment proofing bounds the risk; it
  does not eliminate it.
- **Not what appeared on the screen** (§5), unless the hybrid path was used.
- **Not the time**, beyond our own clock, unless an RFC 3161 token was
  obtained.
- **Not exclusivity of possession** when the credential is syncable — the
  `be`/`bs` flags exist so this is visible rather than assumed.
- **Not a qualified signature** in the eIDAS sense.

A signature scheme that is honest about these is worth more in a dispute than
one that claims more and gets tested.

---

**See also:** [docs/terms.md](terms.md) for what is currently accepted and how,
[docs/tandem.md](tandem.md) for how records reach PDI, and
[docs/media-provenance.md](media-provenance.md) for the watermark credential —
a related but separate idea, signing *content* rather than *consent*.
