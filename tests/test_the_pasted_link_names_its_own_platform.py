"""The pasted link names its own platform.

The field report, verbatim: *"I'm not seeing where to import a data screen
profile with a link."* The door existed and asked for a transcription — pick
the platform from a dropdown, then retype the handle out of the link you are
already holding. A person holds a URL far more often than a bare handle, and
the URL already says everything the form asks for: the host names the
platform, the path names the account.

So the handle field takes the link. What the link says wins over the
dropdown, because the link is the thing being imported; a link whose site is
not a recognised platform is refused with the fix in the sentence, and a
platform front door with no account in it is told apart from a profile page.
"""


def _connect(client, profile_id, **body):
    return client.post(f"/profiles/{profile_id}/social", json=body)


def test_a_pasted_link_sets_platform_and_handle(client, profile_id):
    r = _connect(client, profile_id, platform="x", direction="collect",
                 handle="https://instagram.com/dana.grows")
    assert r.status_code == 201, r.text
    out = r.json()
    # The link said instagram; the dropdown said x; the link wins.
    assert out["platform"] == "instagram"
    assert out["handle"] == "@dana.grows"


def test_the_platforms_own_path_furniture_is_not_the_handle(client,
                                                            profile_id):
    r = _connect(client, profile_id, platform="instagram",
                 direction="collect",
                 handle="https://www.linkedin.com/in/dana-grows/")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["platform"] == "linkedin"
    assert out["handle"] == "@dana-grows"


def test_an_at_prefixed_path_is_still_the_handle(client, profile_id):
    r = _connect(client, profile_id, platform="x", direction="collect",
                 handle="https://tiktok.com/@dana.grows")
    assert r.status_code == 201, r.text
    assert r.json()["handle"] == "@dana.grows"


def test_a_hashtag_is_told_apart_from_an_account(client, profile_id):
    """The field report tried a hashtag where a handle goes. A # names a
    topic; silently storing it would build a connection to nobody."""
    r = _connect(client, profile_id, platform="instagram",
                 direction="collect", handle="#gardening")
    assert r.status_code == 422
    assert "hashtag" in r.json()["detail"]


def test_an_unrecognised_site_is_refused_with_the_fix(client, profile_id):
    r = _connect(client, profile_id, platform="x", direction="collect",
                 handle="https://example.org/dana")
    assert r.status_code == 422
    assert "pick the platform" in r.json()["detail"]


def test_a_front_door_with_no_account_is_told_apart(client, profile_id):
    r = _connect(client, profile_id, platform="x", direction="collect",
                 handle="https://instagram.com/")
    assert r.status_code == 400
    assert "no account" in r.json()["detail"]
