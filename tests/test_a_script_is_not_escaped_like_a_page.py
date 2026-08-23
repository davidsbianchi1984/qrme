"""A script is not escaped like a page.

`_q` builds the JavaScript string literals the signing ceremony drops into a
`<script>` element. It called `html.escape`, which is the right tool for a
page and the wrong one for a script: **a browser does not decode HTML
entities inside a script element**, so escaping there protects nothing and
corrupts the value.

    asked     is the value escaped
    mattered  is it escaped for the place it lands

`Marks & Spencer` reached the reader as `Marks &amp; Spencer` — on the page
whose entire job is showing somebody what they are about to sign, which is
the worst page in this product to render a name wrongly.

The page was safe, but by accident rather than by its own mechanism. The line
written as the real defence — `.replace("</", "<\\/")`, against a literal
`</script` ending the element early — sat *after* an `html.escape` that had
already turned `<` into `&lt;`. It never matched anything and never could.

These hold both halves: the value survives intact, and nothing that reaches
the page can close the script element.
"""

import json

import pytest

from qrme import signing_page
from qrme.signing_page import _q


ROUND_TRIP = [
    "Ada Lovelace",
    "Marks & Spencer",
    "a < b",
    "1 > 0 && true",
    "O'Brien",
    'she said "hello"',
    "naïve café — Ω",
    "back\\slash",
    "</script><img src=x onerror=alert(1)>",
    "line break",
    "para break",
]


@pytest.mark.parametrize("value", ROUND_TRIP)
def test_the_value_survives_the_journey(value):
    """What the reader sees is what was given. A JS string literal is also a
    JSON string, so parsing it back is the same question the browser asks."""
    assert json.loads(_q(value)) == value


@pytest.mark.parametrize("value", ROUND_TRIP)
def test_nothing_in_it_can_be_read_as_markup(value):
    """The literal carries no character an HTML parser treats as a tag."""
    literal = _q(value)
    for char in "<>&":
        assert char not in literal, f"{char!r} reached the page raw"


@pytest.mark.parametrize("value", ROUND_TRIP)
def test_no_javascript_line_terminator_survives(value):
    """U+2028 and U+2029 end a string literal in JavaScript and JSON leaves
    them raw — a value carrying one used to produce a page that did not
    parse."""
    assert " " not in _q(value) and " " not in _q(value)


def test_the_ceremony_page_cannot_be_closed_early():
    """The whole page, with every field hostile: the script element ends
    exactly once, where the template ends it."""
    hostile = "</script><img src=x onerror=alert(1)>"
    page = signing_page.ceremony_page(
        mode="sign", challenge=hostile, rp_id=hostile,
        display_text=hostile, meaning=hostile,
        user_id=hostile, user_name=hostile, display_name=hostile)
    assert page.count("<script>") == 1
    assert page.count("</script>") == 1
    # And the one closer is the last thing before the document ends.
    assert page.index("</script>") > page.index("<script>")


def test_the_signed_text_is_shown_as_written():
    """The document a person is confirming is rendered in the page body, not
    the script — so it is `html.escape`'s job there, and it still is."""
    page = signing_page.ceremony_page(
        mode="sign", challenge="c", rp_id="example.com",
        display_text="Pay Marks & Spencer £5", meaning="a < b")
    assert "Pay Marks &amp; Spencer £5" in page
    assert "a &lt; b" in page
