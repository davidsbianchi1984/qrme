"""What a page promises a browser before it says anything else.

These products serve a handful of HTML pages that a person reaches **without
an account, on a device that is not theirs**: the sticker a stranger kneels
over, the sealed-carrier card, the page a sign-in provider sends a browser
back to. Until 0.59.3 every one of them went out with no
`Content-Security-Policy`, no `X-Content-Type-Options`, no `X-Frame-Options`
and no `Referrer-Policy` — measured over HTTP, because a `TestClient` reads
none of those and a browser reads all of them.

That was the standing invitation. The thing that walked through it was an
unescaped query parameter on the OAuth callback, rendered straight into the
page: `?error=<script>…</script>` came back verbatim, executing on the
product's own origin. Escaping is the fix for that one. This is the layer that
makes the *next* one harmless.

## Why a nonce rather than `'unsafe-inline'`

A CSP with `script-src 'unsafe-inline'` permits exactly the thing an injected
`<script>` needs, and would have stopped nothing above. So the pages that
carry an inline script emit it through :func:`script_open`, which stamps the
per-response nonce, and the policy names that nonce and nothing else. An
injected tag has no nonce and does not run.

`style-src` keeps `'unsafe-inline'`: the stylesheets are constants in this
package, no page interpolates into them, and a nonce there would buy nothing
a reader would ever notice.

    asked     is the page correct
    mattered  what can a page do that is not
"""

from __future__ import annotations

import contextvars
import html
import secrets

#: Set per request, read by the page builders. The same shape the request-key
#: middleware uses, for the same reason: the value belongs to one request and
#: a stale one is a false statement about the next.
_NONCE: contextvars.ContextVar[str] = contextvars.ContextVar(
    "csp_nonce", default="")

#: Sent on every HTML response. Fixed rather than computed: none of them
#: depends on the page.
HEADERS = {
    # Never let a browser second-guess the declared type. An SVG sniffed as
    # HTML is a script; these products serve SVG on public routes.
    "x-content-type-options": "nosniff",
    # A page reached from a QR sticker should not tell the next host where the
    # reader came from — the referrer is the beacon they scanned.
    "referrer-policy": "no-referrer",
    # Belt to the policy's braces, for readers on browsers that predate it.
    "x-frame-options": "DENY",
}


def new_nonce() -> str:
    """Mint the nonce for this request and make it readable downstream."""
    value = secrets.token_urlsafe(16)
    _NONCE.set(value)
    return value


def nonce() -> str:
    return _NONCE.get()


def script_open() -> str:
    """The opening tag for a page's own inline script.

    Falls back to a bare tag when no nonce is set, which happens only when a
    builder is called outside a request — a test, a preview. That page is not
    served to anyone, and a bare tag there fails loudly under the policy
    rather than silently shipping an unprotected one.
    """
    value = nonce()
    return (f'<script nonce="{html.escape(value)}">' if value
            else "<script>")


def policy(value: str) -> str:
    """The Content-Security-Policy for a self-contained page.

    `default-src 'none'` because these pages fetch nothing: no font host, no
    analytics, no CDN. Everything they need is inline or same-origin, so the
    policy can start from nothing and name the exceptions.
    """
    return "; ".join((
        "default-src 'none'",
        "img-src 'self' data:",
        "style-src 'unsafe-inline'",
        f"script-src 'nonce-{value}'" if value else "script-src 'none'",
        "connect-src 'self'",
        "form-action 'self'",
        "base-uri 'none'",
        "frame-ancestors 'none'",
    ))


def console_policy() -> str:
    """The Content-Security-Policy for the packaged console under ``/app``.

    The console is a built bundle, not a server-rendered page: its script and
    stylesheet are same-origin files whose names are stamped at build time,
    so a per-response nonce can never reach them. Served under
    :func:`policy`, the browser refuses the bundle for want of a nonce no
    build step could have known, and the console renders as a dark, empty
    page — HTML 200, nothing running. That is exactly what 0.60.9 first
    shipped to a real host, and no in-process test saw it, because a
    ``TestClient`` reads the policy and enforces none of it.

    So this policy names ``'self'`` where the page policy names a nonce, and
    still refuses inline script — which is what the nonce was for. The other
    sources are the console's own furniture: ``blob:`` for the previews it
    builds from local files and the audio it synthesises, ``media-src`` for
    the footage it plays, ``worker-src`` for the service worker,
    ``manifest-src`` for what a phone reads when the console is added to a
    home screen.
    """
    from . import embeds
    return "; ".join((
        "default-src 'none'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob:",
        # `data:` is the one-sample silent WAV the speech layer plays to
        # unlock audio on a first user gesture (app/src/spoken.ts,
        # SILENCE). Without it every visit logged a CSP violation in the
        # tester's console — the sound still worked through blob: urls,
        # but a red line on every load is a defect report nobody filed.
        "media-src 'self' blob: data:",
        # `blob:` here, and it is not decoration — it is why every avatar
        # in the console rendered as an untextured grey mannequin.
        #
        #     asked     may the console load its own object URLs
        #     mattered  which directive governs the way it loads them
        #
        # A `.glb` carries its textures inside the file. Three.js hands
        # each one to the browser as an object URL and reads it back with
        # `fetch` — and `fetch` is `connect-src`, not `img-src`. So
        # `img-src ... blob:` was granted, looked like the permission the
        # textures needed, and governed nothing: the browser refused the
        # connection, GLTFLoader logged "Couldn't load texture blob:…"
        # once per image, and the model arrived with every `map` null.
        # Lit, shaped, rigged, and the colour of unpainted clay.
        #
        # It rendered that way on every host and in every browser, and no
        # in-process test saw it — a `TestClient` reads this policy and
        # enforces none of it, which is the same blind spot that shipped
        # the missing nonce and the missing `frame-src`. Third time.
        #
        # The grant is narrow: a `blob:` URL is minted by this document,
        # lives in this document, and cannot name anything the document
        # did not already have.
        "connect-src 'self' blob:",
        "manifest-src 'self'",
        "worker-src 'self'",
        # The video players. Absent, `frame-src` fell back to
        # `default-src 'none'` and every press of play was a white
        # rectangle where the browser refused the embed — on a real host
        # only, the same way the nonce bug above shipped: a TestClient
        # reads this policy and enforces none of it. The origins come from
        # the platform allowlist itself (embeds.PLATFORMS), so adding a
        # platform cannot leave the policy behind.
        "frame-src " + " ".join(embeds.embed_origins()),
        "form-action 'self'",
        "base-uri 'none'",
        "frame-ancestors 'none'",
    ))
