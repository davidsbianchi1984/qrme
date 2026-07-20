"""Cloud-contribution transparency: an owner can preview exactly what would
be contributed, see everything that has left, and revoke — which stops future
contributions AND deletes past ones at the gateway by their anonymous refs."""

from tests.test_capabilities import make_interactor, make_profile
from tests.test_cloud import cloud_pair  # noqa: F401


def _chat_and_uprate(client, p, user):
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "tell me a story"})
    return client.post(
        f"/profiles/{p['id']}/interactions/{user}/feedback",
        json={"rating": "up"}).json()


def test_preview_shows_exactly_what_would_leave(cloud_pair):
    client, _ = cloud_pair()
    p = make_profile(client, cloud_contribution=True)
    user = make_interactor(client)
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "hello Dana"})

    view = client.get(f"/profiles/{p['id']}/cloud-contribution").json()
    assert view["opted_in"] is True
    preview = view["preview_next"]
    assert preview["kind"] == "rated_exchange"
    # The preview is fully anonymized: no ids anywhere, persona name replaced.
    text = str(preview)
    assert user not in text and p["id"] not in text and "owner-1" not in text
    assert "Dana" not in text and "PERSONA" in text
    # Nothing has actually left yet — preview is a dry run.
    assert view["contributed"] == []


def test_contributions_are_logged_verbatim(cloud_pair):
    client, fake = cloud_pair()
    p = make_profile(client, cloud_contribution=True)
    user = make_interactor(client)
    assert _chat_and_uprate(client, p, user)["contributed"] is True

    view = client.get(f"/profiles/{p['id']}/cloud-contribution").json()
    assert len(view["contributed"]) == 1
    entry = view["contributed"][0]
    assert entry["revoked"] is False
    # The local log holds exactly the payload the gateway received.
    assert entry["payload"] == fake.contributions[0]
    assert entry["payload"]["ref"] == entry["ref"]


def test_revoke_stops_future_and_deletes_past(cloud_pair):
    client, fake = cloud_pair()
    p = make_profile(client, cloud_contribution=True)
    user = make_interactor(client)
    _chat_and_uprate(client, p, user)
    assert len(fake.contributions) == 1

    out = client.post(
        f"/profiles/{p['id']}/cloud-contribution/revoke").json()
    assert out["opted_in"] is False
    assert out["revoked"] == 1
    assert out["deleted_at_gateway"] is True
    assert fake.contributions == []            # gone at the gateway

    # The local history remembers, marked revoked.
    view = client.get(f"/profiles/{p['id']}/cloud-contribution").json()
    assert view["opted_in"] is False
    assert view["contributed"][0]["revoked"] is True

    # And a fresh up-rating no longer contributes anything.
    r = _chat_and_uprate(client, p, user)
    assert r["contributed"] is False
    assert fake.contributions == []


def test_opted_out_profile_shows_empty_state(cloud_pair):
    client, _ = cloud_pair()
    p = make_profile(client)                   # cloud_contribution defaults off
    view = client.get(f"/profiles/{p['id']}/cloud-contribution").json()
    assert view["opted_in"] is False
    assert view["contributed"] == []
    assert "anonymized" in view["policy"]
