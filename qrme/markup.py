"""The HTML a person may put on their own page, and what is stripped out.

MySpace let people paste arbitrary HTML and CSS into a profile. That is the
feature worth reviving — a page you built yourself, in your own markup, is the
thing people actually remember about it — and it is also the single most
famous stored-XSS hole in the history of the web. In October 2005 the *Samy*
worm used exactly this: script smuggled through a profile's markup, executing
in the browser of everyone who viewed it, adding a million friends in about
twenty hours. It took the site offline.

So the answer here is not "no HTML" and not "any HTML". It is an **allowlist**:
a fixed set of tags and attributes that can lay a page out and style it, and
nothing that can execute, navigate, or reach off the page.

What that means concretely:

* **Tags not on the list are dropped, and their text is kept.** Somebody who
  writes ``<blink>`` loses the tag and keeps the word. Silently removing the
  content along with the tag would look like the editor ate their writing.
* **Every attribute is checked**, not just the tag. ``onclick``, ``onerror``
  and every other ``on*`` handler is where most injection actually lives, and
  a tag allowlist without an attribute allowlist stops none of it.
* **URLs must be http, https, mailto, or a fragment.** ``javascript:`` and
  ``data:`` are both script vectors — the second is the one people forget.
* **No ``<style>`` blocks and no ``@import``**, but ``style=""`` survives on a
  short list of visual properties — including ``background-image``, because a
  background is most of what decorating a page means. A ``url()`` inside CSS is
  held to the same scheme check as ``<img src>``; banning one while allowing
  the other was inconsistent, since both fetch from wherever they point.
  Positioning stays out: colour, spacing, borders and fonts cannot lift an
  element out of the page's own box, and ``position`` can.
* **Frames, objects, embeds, forms and scripts are gone entirely.** A form on
  somebody's profile page is a credential-phishing surface with a friendly
  face on it.

The result is a page somebody can genuinely build, that cannot run code in a
stranger's browser. Anything this module is unsure about, it removes.
"""

from __future__ import annotations

import re
from html import escape
from html.parser import HTMLParser

# Layout and text. Deliberately no <a name>, no <base>, nothing that redefines
# how the rest of the document resolves.
ALLOWED_TAGS: dict[str, set[str]] = {
    "p": set(), "br": set(), "hr": set(),
    "b": set(), "strong": set(), "i": set(), "em": set(), "u": set(),
    "s": set(), "strike": set(), "small": set(), "sub": set(), "sup": set(),
    "mark": set(), "code": set(), "pre": set(), "blockquote": set(),
    "h1": set(), "h2": set(), "h3": set(), "h4": set(),
    "ul": set(), "ol": set(), "li": set(), "dl": set(), "dt": set(),
    "dd": set(),
    "div": set(), "span": set(), "center": set(),
    "table": set(), "thead": set(), "tbody": set(), "tr": set(),
    "td": {"colspan", "rowspan", "align"},
    "th": {"colspan", "rowspan", "align"},
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "width", "height"},
    "marquee": set(),          # the nostalgia tax, and it cannot execute
}

# Allowed on any tag.
GLOBAL_ATTRS = {"style", "class", "title", "align"}

# Inline style properties. Visual only: no position, no z-index, no content,
# no behaviour, nothing that can lift an element out of the page's own box.
ALLOWED_CSS = {
    "color", "background", "background-color", "background-image",
    "font", "font-size", "font-weight", "font-style", "font-family",
    "text-align", "text-decoration", "text-transform", "letter-spacing",
    "line-height", "margin", "margin-top", "margin-bottom", "margin-left",
    "margin-right", "padding", "padding-top", "padding-bottom",
    "padding-left", "padding-right", "border", "border-radius", "border-top",
    "border-bottom", "border-left", "border-right", "width", "max-width",
    "height", "opacity", "box-shadow", "text-shadow", "display",
}

SAFE_SCHEMES = ("http://", "https://", "mailto:", "#", "/")

_CSS_URL = re.compile(r"url\s*\(\s*([^)]+?)\s*\)", re.I)
_CSS_BAD = re.compile(r"(expression|javascript:|@import|behavior|binding)", re.I)


def _safe_url(value: str) -> bool:
    v = value.strip().lower().replace("\t", "").replace("\n", "")
    # `//host/path` is protocol-relative: it looks like a site-relative path
    # and fetches from another host entirely. The leading "/" in SAFE_SCHEMES
    # is for real site-relative paths, and this is the one case where those two
    # are told apart.
    if v.startswith("//"):
        return False
    if v.startswith(SAFE_SCHEMES):
        return True
    # Anything else — javascript:, data:, vbscript:, or a scheme nobody has
    # thought about yet — is refused. Unknown is not the same as harmless.
    return False


def _clean_style(value: str) -> str:
    """Keep the visual declarations; drop everything that can do something."""
    if _CSS_BAD.search(value):
        return ""
    out = []
    for decl in value.split(";"):
        if ":" not in decl:
            continue
        prop, _, val = decl.partition(":")
        prop, val = prop.strip().lower(), val.strip()
        if prop not in ALLOWED_CSS or not val:
            continue
        # url() gets the same treatment <img src> gets, rather than being
        # banned outright. Blocking it while allowing <img> was inconsistent —
        # both fetch from wherever they point — and it cost the one thing a
        # decorated page is actually for: a background image. So the URL inside
        # is extracted and checked against the same scheme list, and anything
        # that is not plainly http, https or a site-relative path is dropped.
        urls = _CSS_URL.findall(val)
        if urls and not all(_safe_url(u.strip("\"'")) for u in urls):
            continue
        out.append(f"{prop}: {val}")
    return "; ".join(out)


class _Sanitiser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.removed: set[str] = set()
        self._open: list[str] = []
        # Content inside these is dropped along with the tag: keeping the text
        # of a <script> would paste the source of an attack onto the page.
        self._muted = 0

    _DROP_CONTENT = {"script", "style", "iframe", "object", "embed", "form",
                     "noscript", "template", "svg", "math", "frameset",
                     "frame", "applet", "link", "meta", "base"}

    def handle_starttag(self, tag, attrs):
        if tag in self._DROP_CONTENT:
            self.removed.add(tag)
            self._muted += 1
            return
        if self._muted:
            return
        if tag not in ALLOWED_TAGS:
            self.removed.add(tag)
            return                      # tag goes, its text stays
        keep = []
        for name, value in attrs:
            name = (name or "").lower()
            value = value or ""
            if name.startswith("on"):
                self.removed.add(f"{tag}[{name}]")
                continue
            if name not in ALLOWED_TAGS[tag] and name not in GLOBAL_ATTRS:
                self.removed.add(f"{tag}[{name}]")
                continue
            if name in ("href", "src") and not _safe_url(value):
                self.removed.add(f"{tag}[{name}]")
                continue
            if name == "style":
                value = _clean_style(value)
                if not value:
                    continue
            keep.append(f'{name}="{escape(value, quote=True)}"')
        void = tag in ("br", "hr", "img")
        self.out.append(f"<{tag}{' ' if keep else ''}{' '.join(keep)}"
                        f"{' /' if void else ''}>")
        if not void:
            self._open.append(tag)
            # An <a> on somebody else's page opens away from the site, and
            # rel stops the new page reaching back through window.opener.
            if tag == "a":
                self.out[-1] = self.out[-1][:-1] + (
                    ' target="_blank" rel="noopener noreferrer nofollow">')

    def handle_endtag(self, tag):
        if tag in self._DROP_CONTENT:
            self._muted = max(0, self._muted - 1)
            return
        if self._muted or tag not in ALLOWED_TAGS:
            return
        if tag in self._open:
            while self._open:
                open_tag = self._open.pop()
                self.out.append(f"</{open_tag}>")
                if open_tag == tag:
                    break

    def handle_data(self, data):
        if not self._muted:
            self.out.append(escape(data, quote=False))

    def close_all(self) -> None:
        while self._open:
            self.out.append(f"</{self._open.pop()}>")


def sanitise(html: str) -> tuple[str, list[str]]:
    """Return (safe html, what was removed).

    The removals are reported rather than swallowed so the editor can tell its
    author *"your <script> was dropped"* instead of quietly handing back a page
    that does less than they wrote.
    """
    parser = _Sanitiser()
    parser.feed(html or "")
    parser.close()
    parser.close_all()
    return "".join(parser.out), sorted(parser.removed)
