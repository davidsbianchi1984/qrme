"""The imported link, finally visited.

A ``collect`` connection has carried the account's public address since the
day it was made — platform plus handle is a URL — and the collect door only
ever stored what the owner pasted. ``POST /social/{cid}/scrape`` goes to the
address and takes what a browser would show anybody: the title, the bio line
in the metadata, the visible text. One source item per visit, with the URL
and the fetch time written into the words themselves.

    asked     can collected content enter the profile
    mattered  can the connection fetch it from the address it was given

The fetch is monkeypatched throughout: these tests are about what the door
does with a page, not about the network. The one path that must never reach
the network at all — an offline deployment — is tested by poisoning the
fetcher so any call would fail loudly.
"""

from qrme import offline, scrape


def _connect(client, profile_id, **body):
    r = client.post(f"/profiles/{profile_id}/social", json=body)
    assert r.status_code == 201, r.text
    return r.json()


_PAGE = """
<html><head><title>Dana Grows (@dana.grows)</title>
<meta property="og:description" content="Market gardener. Tomatoes, compost, patience." />
</head><body>
<script>ignore me entirely</script>
<p>Growing food in a small space since 2019.</p>
</body></html>
"""


def test_scrape_builds_the_profile_from_the_public_page(client, profile_id,
                                                        monkeypatch):
    conn = _connect(client, profile_id, platform="instagram",
                    direction="collect", handle="dana.grows")
    seen = {}

    def fake_fetch(url):
        seen["url"] = url
        return _PAGE
    monkeypatch.setattr(scrape, "fetch", fake_fetch)

    r = client.post(f"/social/{conn['id']}/scrape")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["ingested"] == 1
    assert out["url"] == "https://instagram.com/dana.grows"
    assert seen["url"] == out["url"]
    assert "Dana Grows" in out["title"]

    # The page's words are now source material, provenance included.
    sources = client.get(f"/profiles/{profile_id}/sources").json()
    item = next(s for s in sources if s["kind"] == "social_post")
    assert "instagram" in item["title"] and "Dana Grows" in item["title"]
    body = item["content"]
    assert "Tomatoes, compost, patience" in body      # the metadata bio
    assert "Growing food in a small space" in body    # the visible text
    assert "ignore me entirely" not in body           # scripts are not words
    assert "Fetched from https://instagram.com/dana.grows" in body

    # The connection's count moved, same as a paste.
    listed = client.get(f"/profiles/{profile_id}/social").json()
    assert listed[0]["collected"] == 1


def test_offline_refuses_before_any_socket(client, profile_id, monkeypatch):
    conn = _connect(client, profile_id, platform="x",
                    direction="collect", handle="dana")

    def explode(url):
        raise AssertionError("offline deployment opened a socket")
    monkeypatch.setattr(scrape, "fetch", explode)
    monkeypatch.setattr(offline, "enabled", lambda: True)

    r = client.post(f"/social/{conn['id']}/scrape")
    assert r.status_code == 409
    assert "offline" in r.json()["detail"]


def test_a_connection_without_an_address_is_told_so(client, profile_id):
    conn = _connect(client, profile_id, platform="instagram",
                    direction="collect")
    r = client.post(f"/social/{conn['id']}/scrape")
    assert r.status_code == 400
    assert "handle" in r.json()["detail"]


def test_publish_connections_do_not_scrape(client, profile_id):
    conn = _connect(client, profile_id, platform="instagram",
                    direction="publish", handle="dana.grows")
    r = client.post(f"/social/{conn['id']}/scrape")
    assert r.status_code == 409


def test_a_page_with_nothing_readable_is_a_failure_not_a_source(client,
                                                                profile_id,
                                                                monkeypatch):
    conn = _connect(client, profile_id, platform="instagram",
                    direction="collect", handle="dana.grows")
    monkeypatch.setattr(scrape, "fetch",
                        lambda url: "<html><body><script>x</script></body></html>")
    r = client.post(f"/social/{conn['id']}/scrape")
    assert r.status_code == 502
    sources = client.get(f"/profiles/{profile_id}/sources").json()
    assert not [s for s in sources if s["kind"] == "social_post"]


def test_the_extractor_reads_what_a_reader_would():
    page = scrape.extract(_PAGE)
    assert page["title"] == "Dana Grows (@dana.grows)"
    assert page["description"] == "Market gardener. Tomatoes, compost, patience."
    assert "Growing food" in page["text"]
    assert "ignore me" not in page["text"]
