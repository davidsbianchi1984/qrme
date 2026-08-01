# Windows Hello: the field test

**What this test can prove:** that a real TPM-backed passkey, unlocked by a
real face or fingerprint on a real Windows machine, produces an assertion this
backend verifies — and that the resulting package still verifies afterwards,
from its bytes, without trusting the app.

**What it cannot prove**, and it is worth knowing before you start:

* **Windows verifies; it does not sign.** The system prompt confirms a person
  is present. The signature is made by the TPM-held credential over a
  server-issued challenge, and the whole ceremony runs through **Edge's
  WebAuthn**, in an embedded WebView2 — `native/windows/Views/
  SignaturesPage.xaml.cs` marshals nothing itself. So this exercises Edge's
  WebAuthn stack, Windows Hello as its authenticator, and our verification.
  It does not exercise `webauthn.dll` directly.
* **`basic` is the only tier this page can reach.** `OnSign` asks for
  `"basic"`, because `basic` is what a self-asserted credential may sign and
  self-asserted is all the page can enrol. The `standard` and `high` tiers
  need proofing raised by an attestor — a separate flow, not this test.

---

## 0. The setting that decides whether any of this runs

Read this before booting the Windows box; it is the thing that will otherwise
waste the trip.

A WebAuthn relying party id must be a **domain**. `127.0.0.1` is not one.
Every client here reaches the backend on `http://127.0.0.1:8000` by default,
and `QRME_RP_ID` defaults to `qrme.app` — so out of the box the origin cannot
be a relying party and the id does not match it either. The browser refuses
before the Hello prompt appears.

Two settings fix it, and one of them is not optional:

```powershell
$env:QRME_RP_ID      = "localhost"
$env:QRME_RP_ORIGINS = "http://localhost:8000"
```

`localhost` **is** a domain, resolves to the same backend, and counts as a
secure context with no certificate. The clients now rewrite a loopback IP to
`localhost` when they open the ceremony window, so the page's origin will be
`http://localhost:8000` and the two will match.

If they do not match, the ceremony page refuses itself — an HTML page, in the
embedded WebView, naming the variable to change. If you see *"This origin
cannot sign"*, that is this check, and the message is the fix.

`QRME_RP_ORIGINS` is the server-side allowlist that `verify` checks the
assertion's `clientDataJSON` origin against. Leaving it unset skips that
check; setting it is what makes the test cover it.

---

## 1. What you need

- [ ] A Windows 11 machine with a **TPM 2.0** and **Windows Hello enrolled** —
      face, fingerprint, or PIN. Settings → Accounts → Sign-in options; Hello
      must show as set up, not merely available.
- [ ] **WebView2 Runtime** installed. It ships with Windows 11, but a stripped
      image or a VM may not have it. Without it `EnsureCoreWebView2Async`
      throws and the ceremony panel never appears.
- [ ] The QRME backend on that machine, or reachable from it, on port 8000.
- [ ] The Windows shell built from `native/windows/`.
- [ ] A profile created in the app. `OnEnroll` and `OnSign` both return early
      with *"Create a profile first."* without one.

> **A VM will probably not do.** Hello needs a real TPM and real biometric
> hardware. A VM with a virtual TPM can do a **PIN**, which is a legitimate
> user-verification factor and satisfies `userVerification: 'required'` — so
> the ceremony completes and the package verifies. It just is not the face
> half of the claim. If that is all you have, run it, and record that the
> factor was a PIN.

---

## 2. Start the backend

```powershell
$env:QRME_RP_ID      = "localhost"
$env:QRME_RP_ORIGINS = "http://localhost:8000"
python -m qrme --port 8000
```

Check the door before touching the app:

```powershell
curl.exe "http://localhost:8000/signatures/ceremony?mode=enroll&challenge=abc"
```

- [ ] **200 with HTML** containing `navigator.credentials` → the origin can
      sign. Continue.
- [ ] **421 "This origin cannot sign"** → read the message; it names the
      mismatch. Almost always `QRME_RP_ID` still set to `qrme.app`, or the
      URL fetched on `127.0.0.1` rather than `localhost`.

---

## 3. Enrol a credential

In the app: **Signatures → Register this device**.

- [ ] The ceremony panel appears with the heading *"Register this device for
      signing"* and a **Register with Windows Hello** button.
- [ ] Pressing it raises the **Windows Hello system prompt** — the OS one,
      composited by Windows, not drawn by the app.
- [ ] Completing the gesture makes the panel disappear and the status line
      read **"Registered. This credential can sign: basic."**

Then confirm the record rather than the message:

```powershell
curl.exe -H "Authorization: Bearer $TOKEN" http://localhost:8000/signatures/credentials
```

- [ ] `proofing_level` is `self_asserted` — correct, and the reason
      `can_sign` holds only `basic`.
- [ ] `backed_up` is **false** and `device_bound` is **true** for a TPM
      credential. If Hello was configured to sync through a Microsoft account
      passkey, `backup_eligible` flips and `device_bound` goes false. Neither
      is a failure at the `basic` tier; record which you got, because the
      `high` tier refuses a backup-eligible credential and this is where you
      find out which kind the machine mints.
- [ ] `aaguid` is present and non-zero. A zero AAGUID means the authenticator
      declined to identify itself.

**If the Hello prompt never appears**, the failure is almost always one of:

| What you see | What it is |
| --- | --- |
| Status shows a `NotAllowedError` | the origin/rpId mismatch — go back to §0 |
| Status shows `NotSupportedError` | no platform authenticator; Hello is not enrolled |
| Ceremony panel stays blank | WebView2 Runtime missing |
| Status shows *"Create a profile first."* | no profile; make one |

---

## 4. Sign something

In the app: type a document into the box, add a meaning, press **Sign**.

- [ ] The panel shows **the document text you typed**, verbatim, above the
      button. This is the part worth looking at carefully — the system prompt
      cannot show what is being signed, no passkey prompt can, and the page
      says so in its own note. The text on that page is what the server
      recorded; if it differs from what you typed, stop and report it.
- [ ] The Hello prompt appears again.
- [ ] The status line reads **"Signed — sig_… verifies."**

If it reads *"Signed, but the package does not verify"*, that is the
interesting failure — the assertion was accepted and the package it produced
did not check out. Capture the whole package before anything else.

---

## 5. Verify it as a stranger would

This is the claim in `docs/signatures.md` §2 — that the record stands without
trusting our software — so test it the way a counterparty would: with no
token.

```powershell
curl.exe -H "Authorization: Bearer $TOKEN" http://localhost:8000/signatures/sig_XXXX > pkg.json
curl.exe -X POST -H "content-type: application/json" --data "@pkg.json" `
    http://localhost:8000/signatures/verify
```

- [ ] `valid: true`, **with no `Authorization` header on the verify call**.
- [ ] `user_verified` is `true` — the gesture happened, rather than a silent
      credential being used.
- [ ] `sign_count_regressed` is `false`.
- [ ] The recorded `display_text` matches what the panel showed you in §4.

Then break it on purpose, because a verifier that says yes to everything says
nothing:

- [ ] Change one character of `display_text` in `pkg.json` and re-post.
      `valid` must become **false**. If it stays true, the signature is not
      actually covering the document and that is the whole feature.

---

## 6. Sign a second time

- [ ] Sign a different document with the same credential.
- [ ] `sign_count` in `/signatures/credentials` has **increased**. TPM
      credentials maintain a counter; a counter stuck at zero means the
      authenticator is not providing one, which is allowed by the spec and
      worth recording because it removes one clone-detection signal.
- [ ] `sign_count_regressed` is still false.

---

## What to write down

Whatever happened, these are the facts worth carrying back:

1. Windows build, and whether Hello was **face, fingerprint, or PIN**.
2. Whether the credential came back **device-bound or backup-eligible**.
3. The `aaguid`, which identifies the authenticator model.
4. Whether `sign_count` moved between the two signatures.
5. Any step above that failed, with the status line verbatim — the panel's
   text is the DOMException, and its name is the diagnosis.

Items 2 and 4 decide what the `high` tier can actually require on Windows in
practice, which is the question this test exists to answer beyond "does it
work."
