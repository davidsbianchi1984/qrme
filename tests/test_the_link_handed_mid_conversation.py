"""The link handed mid-conversation.

The scrape door visits the address a social connection has always carried;
this is the other way a link reaches a profile — pasted into the chat box
mid-sentence. The profile either reads the page, through the same
offline-gated fetcher every outbound path uses, or is told plainly that it
did not — because the failure mode that matters here is not a missed fetch,
it is a persona confidently describing a page it never saw.

What the tests hold:

* the page the person handed over reaches the prompt for that turn;
* offline, no socket opens and the prompt says the link was not visited;
* a fetch that fails is admitted in the same words, not papered over;
* a message with no link fetches nothing at all.
"""

from qrme import llm, offline, scrape
from qrme.routers import interaction


class _EchoProvider:
    """Captures the system prompt so a test can read what the profile knew."""

    def __init__(self):
        self.system = None

    def generate(self, system, messages):
        self.system = system
        return "a reply"


def _wire(monkeypatch):
    provider = _EchoProvider()
    monkeypatch.setattr(llm, "provider_for_profile",
                        lambda *a, **kw: provider)
    return provider


_PAGE = """
<html><head><title>Community garden opening</title>
<meta property="og:description" content="Saturday, ribbon at noon." />
</head><body><p>Bring a trowel if you have one.</p></body></html>
"""


def test_the_handed_page_reaches_the_prompt(client, profile_id,
                                            interactor_id, monkeypatch):
    provider = _wire(monkeypatch)
    monkeypatch.setattr(scrape, "fetch", lambda url: _PAGE)
    r = client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id,
        "message": "What do you think of https://example.org/garden ?",
    })
    assert r.status_code == 200, r.text
    assert "https://example.org/garden" in provider.system
    assert "Community garden opening" in provider.system
    assert "Bring a trowel" in provider.system


def test_offline_opens_no_socket_and_says_so(client, profile_id,
                                             interactor_id, monkeypatch):
    provider = _wire(monkeypatch)

    def explode(url):
        raise AssertionError("offline deployment opened a socket")
    monkeypatch.setattr(scrape, "fetch", explode)
    monkeypatch.setattr(offline, "enabled", lambda: True)
    monkeypatch.setattr(interaction.offline, "enabled", lambda: True)

    r = client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id,
        "message": "Look at https://example.org/garden please",
    })
    assert r.status_code == 200, r.text
    assert "offline" in provider.system
    assert "never guess" in provider.system


def test_a_failed_fetch_is_admitted_not_papered_over(client, profile_id,
                                                     interactor_id,
                                                     monkeypatch):
    provider = _wire(monkeypatch)

    def down(url):
        raise OSError("connection refused")
    monkeypatch.setattr(scrape, "fetch", down)

    r = client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id,
        "message": "Did you see https://example.org/garden ?",
    })
    assert r.status_code == 200, r.text
    assert "could not be reached" in provider.system
    assert "never guess" in provider.system


def test_a_message_without_a_link_fetches_nothing(client, profile_id,
                                                  interactor_id, monkeypatch):
    _wire(monkeypatch)

    def explode(url):
        raise AssertionError("fetched with no link in the message")
    monkeypatch.setattr(scrape, "fetch", explode)

    r = client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id,
        "message": "No links today, just hello.",
    })
    assert r.status_code == 200, r.text
