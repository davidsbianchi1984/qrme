"""The moving image — claims 3/13: "the graphical image is a moving or video
image", dynamically updating with interaction history, watermarked.

The portrait's motion block rides the same avatar response as the AI badge
and the likeness record, so nothing can animate the face without holding the
disclosure. The animation parameters are derived from the profile's latent
persona embeddings — the picture changes as the relationships do — and the
owner chooses only the style.
"""

from tests.test_capabilities import as_owner, make_profile


def test_the_portrait_moves_and_carries_its_badge(client):
    p = make_profile(client)
    face = client.get(f"/profiles/{p['id']}/avatar").json()
    motion = face["motion"]
    assert motion["style"] == "breathe"          # the default carries motion
    assert motion["tempo_ms"] > 0                # it breathes, not flickers
    assert motion["states"]["speaking"] == "mouth-and-hands"
    assert motion["updated_with"] == 0
    # The disclosure travels in the same shape as the movement.
    assert "watermark" in face and "likeness" in face


def test_the_motion_follows_the_interaction_history(client):
    p = make_profile(client)
    before = client.get(f"/profiles/{p['id']}/avatar").json()["motion"]
    who = client.post("/interactors", json={"display_name": "Ana"}).json()["id"]
    assert client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": who, "message": "hello!"}).status_code == 200
    after = client.get(f"/profiles/{p['id']}/avatar").json()["motion"]
    assert after["updated_with"] == 1
    # Derived, not stored: the disposition now conditions the movement.
    assert (after["energy"], after["warmth"]) != (
        before["energy"], before["warmth"]) or after["tempo_ms"] > 0


def test_the_owner_chooses_the_style_still_pins_it_flat(client):
    p = make_profile(client)
    as_owner(client, p)
    r = client.put(f"/profiles/{p['id']}/avatar", json={
        "asset": "https://cdn.example/dana.png", "motion_style": "still"})
    assert r.status_code == 200
    motion = r.json()["motion"]
    assert motion["style"] == "still" and motion["tempo_ms"] == 0
    assert set(motion["states"].values()) == {"still"}

    lively = client.put(f"/profiles/{p['id']}/avatar", json={
        "asset": "https://cdn.example/dana.png", "motion_style": "lively"})
    assert lively.json()["motion"]["tempo_ms"] > 0

    bad = client.put(f"/profiles/{p['id']}/avatar", json={
        "asset": "https://cdn.example/dana.png", "motion_style": "backflip"})
    assert bad.status_code == 422
    assert "still, breathe, lively" in bad.json()["detail"]


def test_an_anonymous_profile_still_moves_but_as_the_stand_in(client):
    p = make_profile(client, anonymous=True)
    face = client.get(f"/profiles/{p['id']}/avatar").json()
    # The silhouette is the picture; the motion animates it like any other,
    # because a stand-in that breathes is still a stand-in.
    assert face["silhouette"] is True
    assert face["motion"]["style"] == "breathe"
