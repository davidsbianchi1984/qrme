"""The promise `embeds.py` makes second, and nothing was checking.

`qrme/embeds.py` opens by naming the two things this feature could quietly
stop doing:

    that nothing is copied, and that nothing is requested from the other
    platform until a viewer asks for it.

The first has real tests: `test_nothing_of_the_video_itself_is_copied` reads
the row back and pins its columns. The second has these:

    assert post["video"]["thumbnail"] is None
    assert "until you press play" in entry["video"]["note"]

A field that is `None` and **a sentence promising a request will not happen**.
Neither one would notice a request happening. Add an oEmbed lookup to fetch a
real title tomorrow, keep `thumbnail` at `None`, leave the note alone, and
every test in that file stays green while the module's central claim — *"a
normal embed loads the other site's player as soon as the page renders, which
tells that company you looked, before you decided to"* — quietly stops being
true.

So this file unplugs the network and then does everything a viewer does.

## Why `urlopen` is the right chokepoint

Every outbound call in this codebase goes through `urllib.request.urlopen` —
`cloud.py`, `llm.py`, `oauth.py`, `pdi_client.py` — so patching it is not a
guess about which library a future thumbnail-fetcher would reach for. A
version that used something else would still have to import something else,
and `test_the_module_has_no_second_way_out` is the backstop for that.
"""

import urllib.request

import pytest

from tests.test_capabilities import auth_header, make_profile

VIDEO = "https://youtu.be/dQw4w9WgXcQ"


@pytest.fixture
def no_egress(monkeypatch):
    """Any outbound request at all becomes a loud failure.

    It **records and then raises**, and both halves earn their place. The
    raise makes a fetch loud. The record is what survives the fetch being
    written the way somebody would actually write it —

        try:
            urllib.request.urlopen(thumbnail_url)
        except Exception:
            pass

    which swallows the exception and would leave a raise-only guard green,
    with the request already made and the other company already told. That
    exact shape was run against this file before it was trusted; the raise
    was eaten and the list still failed the test.
    """
    calls = []

    def boom(req, *a, **k):
        url = getattr(req, "full_url", req)
        calls.append(url)
        raise AssertionError(
            f"a request went out to {url} — nothing may be requested from "
            f"the other platform until a viewer presses play")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    return calls


def _post(client, body="Worth eight minutes.", title=None):
    me = make_profile(client, display_name="Poster")
    payload = {"body": body, "video_url": VIDEO}
    if title:
        payload["video_title"] = title
    r = client.post(f"/profiles/{me['id']}/wall", json=payload,
                    headers=auth_header(me))
    assert r.status_code in (200, 201), r.text
    return me, r.json()


def test_posting_a_video_asks_the_other_platform_nothing(client, no_egress):
    """The moment a scraped title or a cached thumbnail would be fetched."""
    _post(client, title="the compounding talk")
    assert no_egress == []


def test_rendering_the_wall_asks_the_other_platform_nothing(client, no_egress):
    """The claim that matters most, because it is the one a viewer cannot see
    being broken. A page that fetches on render tells the other company you
    looked before you decided to."""
    me, _ = _post(client)
    r = client.get(f"/profiles/{me['id']}/wall")
    assert r.status_code == 200, r.text
    assert r.json()["posts"], "no post rendered — the test proved nothing"
    assert no_egress == []


def test_reading_the_post_on_its_own_asks_nothing(client, no_egress):
    me, post = _post(client)
    client.get(f"/profiles/{me['id']}/wall/{post['id']}")
    assert no_egress == []


def test_the_public_feed_asks_the_other_platform_nothing(client, no_egress):
    """The feed autoplays by design, which makes it the surface where a
    render-time fetch would be least noticed and most costly."""
    _post(client)
    client.get("/feed")
    assert no_egress == []


def test_the_facade_still_carries_what_a_viewer_needs(client, no_egress):
    """The other half, so this cannot be satisfied by rendering nothing.

    A guard that only asserts an absence is passed by a feature that has
    stopped working, and "no request went out" is trivially true of a blank
    card.
    """
    me, _ = _post(client, title="the compounding talk")
    video = client.get(f"/profiles/{me['id']}/wall").json()["posts"][0]["video"]
    assert video["platform"]
    assert video["title"] == "the compounding talk"
    assert video["thumbnail"] is None
    assert video["loads_on_press"] is True
    assert "until you press play" in video["note"]
    assert no_egress == []


def test_the_module_has_no_second_way_out():
    """The backstop for a future fetcher that reaches for a different library.

    `urlopen` is the chokepoint every other outbound call in this codebase
    uses, so patching it covers what exists. What it cannot cover is a version
    of this module that imports `httpx` and goes around the patch — so the
    source is read directly.
    """
    import pathlib
    import re

    from qrme import embeds
    src = pathlib.Path(embeds.__file__).read_text(encoding="utf-8")
    for network in ("httpx", "requests", "aiohttp", "urllib.request",
                    "socket", "http.client"):
        assert not re.search(
            rf"^\s*(import\s+{re.escape(network)}\b"
            rf"|from\s+{re.escape(network)}\s+import)", src, re.M), (
            f"embeds.py imports {network} — this module builds a facade out of "
            f"a link and the poster's own words, and has no business making a "
            f"request at all")
