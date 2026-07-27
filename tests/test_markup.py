"""The HTML a person may put on their own page.

MySpace's version of this feature is the most famous stored-XSS hole on the
web: in 2005 the Samy worm smuggled script through profile markup and ran it in
the browser of everyone who looked, adding a million friends in about twenty
hours. The nostalgia is worth reviving; that is not.

So these are mostly attack tests. Each one is a real vector, and each asserts
the same thing: the page survives, the payload does not.
"""

import pytest

from qrme import markup
from tests.test_capabilities import auth_header, make_profile


def clean(html):
    return markup.sanitise(html)[0]


# -- what people actually want -----------------------------------------------

def test_ordinary_markup_survives_intact(client):
    out = clean("<h2>My Corner</h2><p>Some <b>bold</b> and <i>italic</i>.</p>")
    assert out == "<h2>My Corner</h2><p>Some <b>bold</b> and <i>italic</i>.</p>"


def test_the_2004_tags_are_allowed_because_they_cannot_execute(client):
    assert "<marquee>" in clean("<marquee>hello</marquee>")
    assert "<center>" in clean("<center>middle</center>")


def test_visual_css_survives(client):
    out = clean('<div style="color:#f00; font-size:20px; border-radius:8px">x</div>')
    for prop in ("color", "font-size", "border-radius"):
        assert prop in out


def test_a_real_link_survives_and_gets_its_rel(client):
    """`target=_blank` without `rel=noopener` lets the opened page reach back
    through window.opener — a real hijack, and free to prevent."""
    out = clean('<a href="https://example.com">hi</a>')
    assert 'href="https://example.com"' in out
    assert "noopener" in out and "noreferrer" in out


# -- the attacks -------------------------------------------------------------

@pytest.mark.parametrize("payload", [
    "<script>alert(1)</script>",
    "<SCRIPT>alert(1)</SCRIPT>",
    "<img src=x onerror=alert(1)>",
    "<div onclick='alert(1)'>x</div>",
    "<div onmouseover=alert(1)>x</div>",
    '<a href="javascript:alert(1)">x</a>',
    '<a href="JaVaScRiPt:alert(1)">x</a>',
    '<img src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">',
    '<iframe src="//evil.example"></iframe>',
    '<object data="//evil.example"></object>',
    '<embed src="//evil.example">',
    '<svg onload=alert(1)>',
    '<body onload=alert(1)>',
    '<style>@import "//evil.example"</style>',
    '<div style="background:url(//logger.example)">x</div>',
    '<div style="behavior:url(#default#time2)">x</div>',
    '<div style="width:expression(alert(1))">x</div>',
    '<meta http-equiv="refresh" content="0;url=//evil.example">',
    '<base href="//evil.example">',
    '<link rel=stylesheet href="//evil.example">',
])
def test_no_payload_survives(payload):
    out = clean(payload)
    lowered = out.lower()
    for banned in ("<script", "onerror", "onclick", "onload", "onmouseover",
                   "javascript:", "data:text/html", "<iframe", "<object",
                   "<embed", "<svg", "@import", "expression(", "behavior:",
                   "http-equiv", "<base", "<link"):
        assert banned not in lowered, f"{banned!r} survived in {out!r}"


def test_a_form_is_removed_entirely(client):
    """A form on somebody's profile is credential phishing with a friendly
    face on it."""
    out = clean('<form action="//phish"><input name="password"></form>')
    assert "<form" not in out.lower() and "<input" not in out.lower()


def test_an_unknown_tag_loses_the_tag_and_keeps_the_words(client):
    """Removing the text with the tag would look like the editor ate their
    writing."""
    assert clean("<blink>important words</blink>") == "important words"


def test_script_content_goes_with_the_tag(client):
    """Unlike an unknown tag: keeping the body of a <script> would paste the
    source of an attack onto the page as text."""
    assert "steal" not in clean("<script>steal()</script>")


def test_what_was_stripped_is_reported(client):
    """So the editor can say 'your <script> was dropped' rather than quietly
    returning a page that does less than its author wrote."""
    _, removed = markup.sanitise("<script>x</script><blink>y</blink>")
    assert "script" in removed and "blink" in removed


# -- through the API ---------------------------------------------------------

def test_a_page_stores_markup_already_sanitised(client):
    """Cleaned on the way in, so there is exactly one moment unsafe markup
    could exist — before anything is written — rather than one per renderer,
    each of which could forget."""
    from qrme import db
    me = make_profile(client, display_name="Decorator")
    client.put(f"/profiles/{me['id']}/page",
               json={"html": "<p>hi</p><script>alert(1)</script>"},
               headers=auth_header(me))
    stored = db.connect().execute(
        "SELECT html FROM profile_pages WHERE profile_id=?",
        (me["id"],)).fetchone()["html"]
    assert "<script" not in stored.lower()

    shown = client.get(f"/profiles/{me['id']}/page").json()
    assert shown["html"] == stored
    assert "script" in shown["html_removed"]


def test_the_editor_is_told_which_tags_it_may_use(client):
    """So it can grey out what it knows will be stripped, rather than letting
    somebody write it and lose it."""
    r = client.get("/pages/themes").json()
    assert "marquee" in r["html_tags"] and "script" not in r["html_tags"]
    assert "color" in r["css_properties"] and "position" not in r["css_properties"]
