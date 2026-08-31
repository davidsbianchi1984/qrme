"""Every avatar in the console rendered as unpainted clay, and the policy
said it could.

A `.glb` carries its textures inside the file. Three.js hands each one to
the browser as an object URL and reads it back with `fetch` — and `fetch`
is governed by `connect-src`, not by `img-src`.

    asked     may the console load its own object URLs
    mattered  which directive governs the way it loads them

`img-src 'self' data: blob:` was granted, reads exactly like the
permission a texture needs, and governed nothing. The browser refused the
connection, GLTFLoader logged `Couldn't load texture blob:…` once per
image, and the model arrived lit, shaped, rigged, and grey. Every host,
every browser, every avatar.

## Why no test saw it

The same blind spot that shipped a missing nonce and a missing
`frame-src`: a `TestClient` reads this policy and enforces none of it.
Three defects now have reached a real host through the identical gap, so
this file stops testing that the policy *is served* and starts testing
what it *permits* — the shapes the console is known to use, each named
with the thing that breaks without it.

That is still not a browser. It is a statement of intent that a future
tightening has to argue with, which is the part that was missing: the
`blob:` in `img-src` was added deliberately, by somebody who knew the
console builds object URLs, and it went in the wrong directive because
nothing wrote down what the console actually does with them.
"""

from __future__ import annotations

from qrme import pagehead


def _directives(policy: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for piece in policy.split(";"):
        parts = piece.strip().split()
        if parts:
            out[parts[0]] = parts[1:]
    return out


def test_the_console_may_fetch_its_own_object_urls():
    """The avatars. `GLTFLoader` reads a `.glb`'s embedded textures back
    through `fetch` on a `blob:` URL, so this is the directive that
    decides whether a face has skin on it."""
    assert "blob:" in _directives(pagehead.console_policy())["connect-src"]


def test_the_console_may_draw_its_own_object_urls():
    """The other half, and the one that was already right: a preview built
    from a file somebody picked goes into an `<img>`."""
    assert "blob:" in _directives(pagehead.console_policy())["img-src"]


def test_the_console_may_play_its_own_object_urls():
    """Synthesised speech arrives as a blob and is played, not fetched."""
    media = _directives(pagehead.console_policy())["media-src"]
    assert "blob:" in media and "data:" in media


def test_the_console_still_refuses_a_stranger():
    """The grant is narrow on purpose. A `blob:` URL is minted by this
    document and cannot name anything the document did not already have —
    which is why widening `connect-src` to it costs nothing, and why
    widening it to a host would cost everything."""
    connect = _directives(pagehead.console_policy())["connect-src"]
    assert set(connect) == {"'self'", "blob:"}


def test_the_self_contained_pages_stay_shut():
    """The other policy fetches nothing and keeps its `default-src 'none'`.
    A fix on the console is not a licence to loosen the page beside it."""
    page = _directives(pagehead.policy("a-nonce"))
    assert page["default-src"] == ["'none'"]
    assert page["connect-src"] == ["'self'"]
    assert "blob:" not in page["img-src"]
