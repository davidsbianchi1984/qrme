"""Synthetic-media watermarking: generated content leaving the platform
carries a verifiable credential — who produced it, what it is, and a hash
that catches tampering. Verification is public by design."""

from tests.conftest import ADULT_VERIFICATION


def _profile(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "self", "display_name": "Dana",
        "persona": "A retired teacher who loves gardening.",
        "verification": ADULT_VERIFICATION})
    body = r.json()
    client.headers["authorization"] = f"Bearer {body['owner_token']}"
    return body["id"]


def test_posts_carry_a_verifiable_watermark(client):
    pid = _profile(client)
    post = client.post(f"/profiles/{pid}/compose",
                       json={"topic": "spring planting"}).json()
    wm = post["watermark"]
    assert wm["kind"] == "post" and wm["profile_id"] == pid
    assert "synthetic" in wm["disclosure"]

    # The public credential resolves without any token.
    client.headers.pop("authorization", None)
    cred = client.get(f"/watermarks/{wm['watermark_id']}").json()
    assert cred["valid"] is True
    assert cred["content_sha256"] == wm["content_sha256"]

    # Presenting the genuine content matches; altered content is caught.
    genuine = client.post("/watermarks/verify", json={
        "watermark_id": wm["watermark_id"],
        "content": post["content"]}).json()
    assert genuine["content_match"] is True
    tampered = client.post("/watermarks/verify", json={
        "watermark_id": wm["watermark_id"],
        "content": post["content"] + " …with words nobody wrote"}).json()
    assert tampered["content_match"] is False
    assert "altered" in tampered["note"]

    # The stored post keeps its credential reference.
    posts = client.get(f"/profiles/{pid}/posts").json()
    assert posts[0]["watermark_id"] == wm["watermark_id"]


def test_non_text_chat_modalities_are_watermarked(client):
    pid = _profile(client)
    i = client.post("/interactors", json={"display_name": "Sam"}).json()
    r = client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": i["id"], "message": "say hi",
        "modality": "voice"}).json()
    wm = r["modality"]["watermark"]
    assert wm["kind"] == "voice" and wm["profile_id"] == pid
    assert client.get(f"/watermarks/{wm['watermark_id']}").json()["valid"]

    # Plain text replies carry no media watermark (no non-text media exists).
    plain = client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": i["id"], "message": "again"}).json()
    assert plain["modality"] is None


def test_unknown_watermark_fails_the_lookup(client):
    _profile(client)
    assert client.get("/watermarks/wmk_never_issued").status_code == 404
    r = client.post("/watermarks/verify",
                    json={"watermark_id": "wmk_never_issued", "content": "x"})
    assert r.status_code == 404

def test_every_text_reply_is_watermarked_with_visible_mark(client):
    pid = _profile(client)
    i = client.post("/interactors", json={"display_name": "Sam"}).json()
    r = client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": i["id"], "message": "tell me about your garden"}).json()
    wm = r["profile_message"]["watermark"]
    assert wm is not None and wm["kind"] == "chat"
    assert "AI" in wm["display"]["line"]
    assert wm["display"]["always_displayed"] is True
    assert client.get(f"/watermarks/{wm['watermark_id']}").json()["valid"]

    # The stored history renders with the same mark.
    client.headers["authorization"] = f"Bearer {i['token']}"
    history = client.get(
        f"/profiles/{pid}/memory/{i['id']}").json()
    profile_turns = [m for m in history if m["role"] == "profile"]
    assert profile_turns and all(
        m["watermark"]["display"]["line"].startswith("✦")
        for m in profile_turns)

    # The interactor's own words are not watermarked — only AI renders are.
    assert all(m["watermark"] is None
               for m in history if m["role"] == "interactor")


def test_custom_watermark_design_always_declares_ai(client):
    pid = _profile(client)
    # The owner designs a custom mark — but the AI designation is invariant.
    design = client.put(f"/profiles/{pid}/watermark", json={
        "mark": "🌹", "label": "Dana's Garden"}).json()
    assert design["custom"] is True
    assert design["line"] == "🌹 AI · Dana's Garden"

    # Everything generated from now on renders with the custom design.
    post = client.post(f"/profiles/{pid}/compose",
                       json={"topic": "roses"}).json()
    assert post["watermark"]["display"]["line"] == "🌹 AI · Dana's Garden"

    # The design is public (any surface must render it); changing it is not.
    owner_token = client.headers.pop("authorization")
    assert client.get(f"/profiles/{pid}/watermark").json()["line"] \
        == "🌹 AI · Dana's Garden"
    assert client.put(f"/profiles/{pid}/watermark",
                      json={"label": "not yours"}).status_code == 401
    client.headers["authorization"] = owner_token

    # Clearing both fields resets to the default design.
    reset = client.put(f"/profiles/{pid}/watermark", json={}).json()
    assert reset["custom"] is False and reset["line"] == "✦ AI · Dana"


def test_creative_works_and_guidance_are_stamped(client):
    pid = _profile(client)
    work = client.post(f"/profiles/{pid}/assist/compose", json={
        "kind": "poem", "moment": "first bloom of spring"}).json()
    assert work["watermark"]["kind"] == "poem"
    assert "AI" in work["watermark"]["display"]["line"]
    listed = client.get(f"/profiles/{pid}/assist/works").json()
    assert listed[0]["watermark"]["watermark_id"] \
        == work["watermark"]["watermark_id"]

    edited = client.post(f"/profiles/{pid}/assist/proofread",
                         json={"text": "i think the garden are lovely"}).json()
    assert edited["watermark"]["kind"] == "proofread"


def test_an_anonymous_profiles_watermark_does_not_name_it(client):
    """The anonymity toggle withholds the display name from summon cards and
    marketplace listings. The default watermark is built from that same name
    and rides on every render the profile produces, so it was the one surface
    that gave it away — found by a beacon scan, where the leak would have been
    to a stranger who scanned a sticker."""
    body = {"owner_id": "o1", "kind": "fictional", "display_name": "Marcus Bell",
            "persona": "A retired planner.", "anonymous": True,
            "verification": {"birthdate": "1980-01-01",
                             "id_document": "passport", "liveness_check": True}}
    pid = client.post("/profiles", json=body).json()["id"]

    design = client.get(f"/profiles/{pid}/watermark").json()
    assert "Marcus Bell" not in design["line"]
    from qrme import identity
    assert design["line"] == f"\u2726 AI \u00b7 {identity.anonymous_name(pid)}"
    assert "Anonymous " in design["line"]

    # Still declares AI, which is the part that is never negotiable.
    assert "AI" in design["line"]


def test_a_named_profiles_watermark_still_names_it(client):
    body = {"owner_id": "o1", "kind": "fictional", "display_name": "Ada",
            "persona": "An engineer.",
            "verification": {"birthdate": "1980-01-01",
                             "id_document": "passport", "liveness_check": True}}
    pid = client.post("/profiles", json=body).json()["id"]
    assert client.get(f"/profiles/{pid}/watermark").json()["line"].endswith("Ada")
