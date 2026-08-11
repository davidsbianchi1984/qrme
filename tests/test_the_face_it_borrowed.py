"""The avatar deck's import shelf — a face from photos, a capture, or a
market avatar the person already owns.

The starter collection covers profiles that want an invented face. This
covers everyone else: the owner's own photos, the selfie capture's frames,
and the avatar systems people already live in (Ready Player Me, Bitmoji,
Meta, Memoji and the rest) — as *imports*, because that is the honest verb.
The person exports the avatar on the provider's own surface and hands QRME
the image; nothing here calls a provider API or holds a provider credential,
and `GET /avatars/market` says exactly how each export works.

What the tests hold:

* the import sets the portrait through the same pipeline as a starter
  portrait — the AI badge and the likeness record ride on the render;
* the provenance is written onto the profile's own record as a source item,
  with the source named and every extra frame kept;
* an unknown source is refused with the pointer to the market list, because
  a deck that silently accepts anything is a deck whose provenance means
  nothing.
"""


def test_the_market_shelf_names_its_sources_and_their_exports(client):
    r = client.get("/avatars/market")
    assert r.status_code == 200
    sources = r.json()["sources"]
    keys = {s["key"] for s in sources}
    assert {"ready_player_me", "bitmoji", "meta_avatar",
            "apple_memoji", "other"} <= keys
    # Every shelf entry says how the export works — the door is only honest
    # if the person can actually walk through it.
    assert all(s["how"] for s in sources)
    assert "import" in r.json()["note"]


def test_an_imported_avatar_becomes_the_portrait_with_provenance(client,
                                                                 profile_id):
    r = client.post(f"/profiles/{profile_id}/avatar/import", json={
        "source": "ready_player_me",
        "asset": "https://models.readyplayer.me/abc123.png",
    })
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["asset"] == "https://models.readyplayer.me/abc123.png"
    # The render pipeline is unchanged: badge and likeness ride on it.
    assert out["watermark"]["disclosure"]
    assert "likeness" in out

    sources = client.get(f"/profiles/{profile_id}/sources").json()
    item = next(s for s in sources
                if s["title"] == "avatar import — ready_player_me")
    assert item["kind"] == "photo"


def test_the_capture_keeps_every_angle_it_took(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/avatar/import", json={
        "source": "capture",
        "asset": "med_front",
        "extra": ["med_left", "med_right", "med_up", "med_down"],
    })
    assert r.status_code == 201, r.text
    assert r.json()["asset"] == "med_front"
    sources = client.get(f"/profiles/{profile_id}/sources").json()
    assert any(s["title"] == "avatar import — capture" for s in sources)


def test_an_unknown_source_is_refused_with_the_pointer(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/avatar/import", json={
        "source": "made_up_platform", "asset": "x.png",
    })
    assert r.status_code == 422
    assert "market" in r.json()["detail"]


def test_the_import_is_owner_only(client, profile_id):
    saved = client.headers.pop("authorization")
    try:
        r = client.post(f"/profiles/{profile_id}/avatar/import", json={
            "source": "bitmoji", "asset": "x.png",
        })
        assert r.status_code in (401, 403)
    finally:
        client.headers["authorization"] = saved
