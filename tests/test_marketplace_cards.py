"""Discovery cards carry the portrait — and say which kind of face it is."""

from tests.conftest import client  # noqa: F401 — the standard app fixture


def test_marketplace_cards_carry_the_portrait_and_its_provenance(client):
    client.post("/marketplace/seed")
    cards = client.get("/marketplace").json()
    assert cards, "the starter collection should list"
    with_portrait = [c for c in cards if c.get("avatar")]
    assert with_portrait, "starters ship burned portraits"
    for card in cards:
        assert "avatar" in card and "avatar_kind" in card
        if card["avatar"] is None:
            assert card["avatar_kind"] is None
        else:
            # A generated face is labelled "ai"; only an authentic photograph
            # under /photos may say "real_photo".
            assert card["avatar_kind"] in ("ai", "real_photo")
            if card["avatar"].startswith("/portraits/"):
                assert card["avatar_kind"] == "ai"
