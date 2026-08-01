# Sign in with Google and Apple — field by field

**Status: implemented** in `qrme/oauth.py` and `qrme/routers/accounts.py`.
Nothing in this document is code to write. It is the console work, with the
exact value for every field, and the two things about it that are not
obvious.

The buttons are already in the console. `GET /auth/oauth/providers` reports
each one as `configured: false` with a `setup` line, and `Onboarding.tsx`
greys the button and shows the reason — a working-looking button that
dead-ends is worse than an honest grey one. Filling in the four environment
variables below is the whole job.

| Variable | Provider | What it is |
| --- | --- | --- |
| `QRME_GOOGLE_CLIENT_ID` | Google | the OAuth client ID, ends `.apps.googleusercontent.com` |
| `QRME_GOOGLE_CLIENT_SECRET` | Google | a string, copied once, no expiry |
| `QRME_APPLE_CLIENT_ID` | Apple | the **Services ID** identifier, e.g. `app.qrme.signin` |
| `QRME_APPLE_CLIENT_SECRET` | Apple | a **JWT you sign yourself**, expires within six months |

That last row is the whole reason this document is longer than a list.

---

## 1. Before either console: decide the return address

Both providers check that the browser comes back to an address you
registered in advance. That address is this API's own callback:

```
{base}/auth/oauth/{provider}/callback
```

`oauth_start` fills `{base}` in from the incoming request, so it is whatever
the console reached the backend on. In practice there are two:

* **Desktop app** — the backend answers on loopback, so the return address is
  `http://127.0.0.1:8000/auth/oauth/google/callback`. Google's desktop
  clients accept loopback. **Apple does not accept it at all.**
* **Hosted deployment** — `https://your-host/auth/oauth/google/callback` and
  the Apple equivalent.

**Apple requires https and a real domain.** There is no loopback exemption
and no self-signed allowance. If QRME is only ever run as a desktop app on
someone's machine, Google sign-in works and Apple sign-in cannot — that is a
constraint of Apple's, not a gap here, and `providers()` says so in its
`setup` string. To offer Apple you need the hosted deployment you are
standing up for cloudgw anyway.

---

## 2. Google — console.cloud.google.com

Roughly ten minutes. The account that does this owns the client forever, so
use one that outlives any individual.

**a. Project.** *Select a project → New project.* Name it `QRME`. Nothing
else on that page matters.

**b. Branding** (*APIs & Services → OAuth consent screen → Branding*).

| Field | Value |
| --- | --- |
| App name | `QRME` |
| User support email | your address |
| App logo | optional — skip it; uploading one triggers a verification review |
| Application home page | `https://qrme.app` (or your host) |
| Privacy policy link | required before publishing — the terms page you already have |
| Authorized domains | the bare domain, `qrme.app`. No scheme, no path. |
| Developer contact | your address |

**c. Audience.** *External.* While it is in **Testing** only accounts on the
test-users list can sign in, and it is capped at 100 — fine for a field test,
not fine for release. Press **Publish app** when you are done testing. With
only the three scopes below there is no verification review to wait for.

**d. Data access → scopes.** Add exactly three:

```
openid
.../auth/userinfo.email
.../auth/userinfo.profile
```

These are the three `qrme/oauth.py` requests (`openid email profile`). They
are "non-sensitive" in Google's classification, which is what keeps this out
of the review queue. **Do not add anything else** — one sensitive scope turns
a ten-minute task into a multi-week verification.

**e. Clients → Create client.**

| Field | Value |
| --- | --- |
| Application type | **Web application** |
| Name | `QRME backend` |
| Authorized JavaScript origins | *leave empty* — the browser never posts to Google from our page |
| Authorized redirect URIs | see below |

Add every return address the deployment will actually use:

```
http://127.0.0.1:8000/auth/oauth/google/callback
https://your-host/auth/oauth/google/callback
```

Google matches these **exactly** — trailing slash, scheme, port and all.
`localhost` and `127.0.0.1` are different strings to Google; the code sends
whatever `request.url_for` produced, so register the one your deployment
answers on. If in doubt register both.

> **Web application, not Desktop app.** The Desktop-app client type looks
> right for an Electron console and is wrong: it issues no client secret, and
> `_exchange` posts `client_secret` on every token call. A Desktop-app client
> makes `QRME_GOOGLE_CLIENT_SECRET` un-fillable.

**f. Copy both values** into the environment:

```bash
QRME_GOOGLE_CLIENT_ID=1234567890-abc….apps.googleusercontent.com
QRME_GOOGLE_CLIENT_SECRET=GOCSPX-…
```

Restart the backend. `GET /auth/oauth/providers` should now report Google as
`configured: true`, and the button in Onboarding goes live.

---

## 3. Apple — developer.apple.com

Needs a paid Apple Developer Program membership. Four objects, in order,
because each one needs the one before it.

**a. Note your Team ID.** *Membership details*, top right — ten characters,
e.g. `A1B2C3D4E5`. It becomes the `iss` claim of the secret.

**b. App ID** (*Certificates, Identifiers & Profiles → Identifiers → + →
App IDs → App*).

| Field | Value |
| --- | --- |
| Description | `QRME` |
| Bundle ID | Explicit, `app.qrme.studio` |
| Capabilities | tick **Sign In with Apple** |

You are not shipping an iOS app through this door, but Apple requires an App
ID to exist as the primary of the group before a Services ID can use it.

**c. Services ID** (*Identifiers → + → **Services IDs***).

| Field | Value |
| --- | --- |
| Description | `QRME Sign In` |
| Identifier | `app.qrme.signin` — **this is `QRME_APPLE_CLIENT_ID`** |

Save, then re-open it, tick **Sign In with Apple**, press **Configure**:

| Field | Value |
| --- | --- |
| Primary App ID | the App ID from (b) |
| Domains and Subdomains | `your-host` — bare domain, no scheme |
| Return URLs | `https://your-host/auth/oauth/apple/callback` |

The Services ID identifier is *not* the App ID. They look alike and both are
reverse-DNS strings; using the App ID as `QRME_APPLE_CLIENT_ID` produces
`invalid_client` at the exchange with no other clue.

**d. Key** (*Keys → + →* tick **Sign In with Apple** → *Configure* → primary
App ID → *Continue* → *Register*).

Download the `.p8`. **Apple lets you download it once.** Note the **Key ID**
shown on the page — it is also in the filename, `AuthKey_F6G7H8I9J0.p8`.

Put the file somewhere outside this repository. `.gitignore` covers `*.p8`
and a test fails if one lands inside anyway, but the real protection is not
putting it there: a committed key is disclosed whether or not the commit is
reverted, and recovering means revoking the key and re-minting with a new
Key ID.

**e. Mint the secret.**

```bash
python scripts/mint_apple_secret.py mint \
  --team-id A1B2C3D4E5 \
  --key-id F6G7H8I9J0 \
  --services-id app.qrme.signin \
  --key ~/keys/AuthKey_F6G7H8I9J0.p8
```

It prints the JWT on stdout and the expiry date on stderr, so
`… mint … > secret.txt` captures the token alone.

```bash
QRME_APPLE_CLIENT_ID=app.qrme.signin
QRME_APPLE_CLIENT_SECRET=eyJhbGciOiJFUzI1NiIs…
```

---

## 4. The Apple secret expires, and nothing tells you

Apple caps the client secret at six months. There is no renewal notice, no
warning banner, and no degraded mode. On the expiry date the token exchange
starts answering `invalid_client` and Sign in with Apple stops working for
everyone at once.

The check every other part of this system makes is the wrong one:

```
asked     is QRME_APPLE_CLIENT_SECRET set
mattered  is QRME_APPLE_CLIENT_SECRET going to work tomorrow
```

`providers()` asks the first. It stays `true` forever. So does any deployment
health check that greps the environment.

**Ask the second one instead:**

```bash
python scripts/mint_apple_secret.py check --secret "$QRME_APPLE_CLIENT_SECRET"
```

It prints the expiry and the days remaining, needs no `.p8` — the expiry is
in the payload, which is base64, not encryption — and **exits non-zero**
inside the last thirty days or after expiry. That exit code is the point:
wire it into whatever already watches the deployment.

```cron
0 9 * * 1  /usr/bin/python3 /srv/qrme/scripts/mint_apple_secret.py \
             check --secret "$QRME_APPLE_CLIENT_SECRET" || \
             mail -s "QRME: Apple sign-in secret expiring" you@example.com
```

Re-minting is step (e) again with the same three identifiers and the same
`.p8`. Nothing in Apple's console changes and no user is signed out — the
secret authenticates *us to Apple*, not users to us.

---

## 5. What to check once both are set

```bash
curl -s https://your-host/auth/oauth/providers | python3 -m json.tool
```

Both entries should read `"configured": true` and carry no `setup` line. Then
press each button in Onboarding and complete a real sign-in. Two things worth
watching, because they are the failures that look like something else:

* **Apple comes back as a POST.** Requesting any scope forces
  `response_mode=form_post`, so the browser returns with the code in a
  urlencoded body. `oauth_callback_post` handles it. A proxy in front of the
  deployment that only forwards `GET` to `/auth/oauth/…` will turn this into
  a 405 that reads like a routing bug.
* **Apple sends the email once.** On the very first authorization for a given
  Apple ID, and never again. A test account you have already used will come
  back with no email, and `callback` refuses with *"Apple returned no email
  address"* — which is correct, and is not a regression. To retest, revoke
  the app under *Settings → Apple ID → Sign in with Apple* on the device.

Offline mode refuses both by design: `_exchange` raises before the outbound
call, because a token exchange is a request leaving the host.
