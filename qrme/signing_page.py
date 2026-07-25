"""The WebAuthn ceremony, as a page a host application can embed.

iOS and Android reach a platform authenticator through a native API. Windows
has one too — Windows Hello — but the only in-process route to it is
`webauthn.dll`, several hundred lines of version-sensitive struct marshalling
that a compile cannot meaningfully check and that nothing here can execute. A
signing button built on unverified interop looks like it works and might not,
which is worse than no button.

So the ceremony runs where a correct implementation already exists: the
browser engine. The desktop app hosts a WebView2 pointed at this page, the
page calls ``navigator.credentials``, and the result comes back as a message.
Nothing is marshalled by hand; the risky part is Edge's job, and Edge already
talks to Windows Hello.

Three things make this work rather than merely compile:

* **It must be served from the relying party's own origin.** WebAuthn refuses
  a mismatched `rpId`, and an opaque origin (a `data:` URL, a local file) has
  no origin to match. That is why this is a server route and not a string
  embedded in the C#.
* **It never sees a token.** The page runs the ceremony and posts the raw
  assertion to its host; the host makes the authenticated API call. A bearer
  token in a query string would end up in logs and history.
* **It shows the document.** Same reason the native screens do: the system
  prompt cannot say what is being signed, so the last thing on screen before
  it appears is the text the server recorded.
"""

from __future__ import annotations

import html

_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d0a20;color:#f4f1ff;min-height:100dvh;padding:28px;
 font:15px/1.55 -apple-system,'Segoe UI',Roboto,sans-serif}
main{max-width:520px;margin:0 auto;display:flex;flex-direction:column;gap:18px}
h1{font-size:19px}
.doc{background:#181233;border:1px solid #2a2250;border-radius:14px;
 padding:16px;white-space:pre-wrap;word-break:break-word;max-height:38vh;
 overflow:auto;font-size:14px}
.meaning{color:#a79fd0;font-size:13px}
button{width:100%;padding:15px;border:0;border-radius:14px;font-size:15px;
 font-weight:700;color:#fff;background:linear-gradient(120deg,#7c5cff,#4d8dff);
 cursor:pointer}
button:disabled{opacity:.55;cursor:default}
.note{color:#6f6899;font-size:12px}
.err{color:#ff8a80;font-size:13px;white-space:pre-wrap}
"""

# The page posts one message and stops. `chrome.webview` is the WebView2
# host channel; the `opener` branch keeps it usable from an ordinary browser
# window, which is how it gets exercised without a desktop app attached.
_JS = """
const B = {
  enc: b => btoa(String.fromCharCode(...new Uint8Array(b)))
    .replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,''),
  dec: s => Uint8Array.from(
    atob(s.replace(/-/g,'+').replace(/_/g,'/')
      .padEnd(s.length + (4 - s.length %% 4) %% 4, '=')), c => c.charCodeAt(0)),
};

function send(payload) {
  const text = JSON.stringify(payload);
  if (window.chrome && window.chrome.webview) window.chrome.webview.postMessage(text);
  else if (window.opener) window.opener.postMessage(text, '*');
  else console.log(text);
}

async function run() {
  const btn = document.getElementById('go');
  const err = document.getElementById('err');
  btn.disabled = true; err.textContent = '';
  try {
    const challenge = B.dec(%(challenge)s);
    let out;
    if (%(is_enroll)s) {
      const cred = await navigator.credentials.create({publicKey: {
        challenge,
        rp: {id: %(rp_id)s, name: 'QRME'},
        user: {id: B.dec(%(user_id)s), name: %(user_name)s,
               displayName: %(display_name)s},
        pubKeyCredParams: [{type:'public-key',alg:-7},{type:'public-key',alg:-257}],
        authenticatorSelection: {userVerification:'required', residentKey:'required'},
        attestation: 'direct',
      }});
      out = {mode:'enroll', credential_id: B.enc(cred.rawId),
             attestation_object: B.enc(cred.response.attestationObject),
             client_data_json: B.enc(cred.response.clientDataJSON)};
    } else {
      const cred = await navigator.credentials.get({publicKey: {
        challenge, rpId: %(rp_id)s, userVerification: 'required',
      }});
      out = {mode:'sign', credential_id: B.enc(cred.rawId),
             signature: B.enc(cred.response.signature),
             authenticator_data: B.enc(cred.response.authenticatorData),
             client_data_json: B.enc(cred.response.clientDataJSON)};
    }
    send({ok: true, ...out});
    btn.textContent = 'Done — you can close this';
  } catch (e) {
    // Surfaced rather than swallowed: the usual failure here is a relying
    // party that does not match the origin, and a silent button teaches
    // nobody that.
    err.textContent = String(e && e.message ? e.message : e);
    send({ok: false, error: String(e)});
    btn.disabled = false;
  }
}
document.getElementById('go').addEventListener('click', run);
"""


def _q(value: str) -> str:
    """A JS string literal, safe to drop into the script."""
    return html.escape(
        __import__("json").dumps(value), quote=False).replace("</", "<\\/")


def ceremony_page(mode: str, challenge: str, rp_id: str,
                  display_text: str = "", meaning: str = "",
                  user_id: str = "", user_name: str = "",
                  display_name: str = "") -> str:
    """The page a host embeds to run one ceremony."""
    is_enroll = mode == "enroll"
    heading = ("Register this device for signing" if is_enroll
               else "Confirm what you are signing")
    body_doc = ("" if is_enroll else
                f'<div class="doc">{html.escape(display_text)}</div>')
    body_meaning = ("" if is_enroll or not meaning else
                    f'<p class="meaning">{html.escape(meaning)}</p>')
    script = _JS % {
        "challenge": _q(challenge), "rp_id": _q(rp_id),
        "is_enroll": "true" if is_enroll else "false",
        "user_id": _q(user_id), "user_name": _q(user_name),
        "display_name": _q(display_name),
    }
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{html.escape(heading)}</title><style>{_CSS}</style></head>"
        f'<body><main><h1>{html.escape(heading)}</h1>'
        f"{body_doc}{body_meaning}"
        f'<button id="go">{"Register" if is_enroll else "Sign"} with '
        'Windows Hello</button>'
        '<p class="note">The system prompt cannot show what you are signing — '
        'no passkey prompt can. The text above is exactly what the server '
        'recorded.</p>'
        '<p class="err" id="err"></p></main>'
        f"<script>{script}</script></body></html>")
