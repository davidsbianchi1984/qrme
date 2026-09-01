"""The connected-apps connector catalog."""

from qrme import catalog


def test_catalog_endpoint(client):
    body = client.get("/connectors/catalog").json()
    providers = {p["provider"] for p in body["app_providers"]}
    assert providers == {"apple", "google", "microsoft", "canva",
                         "glasses", "gaming", "work", "search", "scrape"}
    assert body["provider_count"] == 9
    assert body["app_count"] == len(catalog.CONNECTORS)


def test_every_provider_has_a_name_a_person_reads():
    """A provider key is a slug; the storefront shows the label.

    The catalog grew a family at a time and the label map is edited
    separately from the rows, so a section added without its label
    ships a heading that reads ``scrape`` to whoever opens the shop.
    """
    for c in catalog.CONNECTORS:
        assert c["provider"] in catalog._PROVIDER_LABEL, c["provider"]
    assert set(catalog._PROVIDER_LABEL) == {
        c["provider"] for c in catalog.CONNECTORS}


def test_every_entry_is_well_formed():
    for c in catalog.CONNECTORS:
        assert c["capabilities"], f"{c['app']} has no capabilities"
        assert c["directions"], f"{c['app']} has no directions"
        assert set(c["directions"]) <= {"collect", "act", "produce"}


def test_a_scrape_row_can_only_read():
    """The social rows read a public page. They do not post.

    ``routers/social.py`` is how a profile *appears* on a platform, and
    everything it publishes goes through the same moderation pipeline as
    chat. A catalog row that named a platform and carried ``act`` would be
    that same power on a second path, reached from the storefront, with no
    moderation behind it — the shape this estate keeps finding and removing.

        asked     can the profile read Instagram
        mattered  can the storefront become a second way to post to it
    """
    for c in catalog.CONNECTORS:
        if c["provider"] == "scrape":
            assert c["directions"] == ["collect"], c["app"]


def test_the_scraped_platforms_are_the_platforms_social_knows():
    """Two halves of one platform list, named once.

    ``social.py`` maps a pasted link's host to a platform slug; the scrape
    rows say what may be read from that platform. If the two spell a
    platform differently, a person connects ``x`` in one place and
    ``twitter`` in the other and the profile holds two of them.
    """
    from qrme.routers import social

    scraped = {c["app"] for c in catalog.CONNECTORS if c["provider"] == "scrape"}
    assert scraped <= set(social._HOST_PLATFORM.values()), (
        scraped - set(social._HOST_PLATFORM.values()))


def test_key_apps_present():
    keys = set(catalog.BY_KEY)
    for expected in [("apple", "photos"), ("apple", "calendar"), ("apple", "mail"),
                     ("apple", "messages"), ("google", "gmail"), ("google", "chrome"),
                     ("microsoft", "file_explorer"), ("microsoft", "m365"),
                     ("canva", "magic_studio")]:
        assert expected in keys, f"missing {expected}"
