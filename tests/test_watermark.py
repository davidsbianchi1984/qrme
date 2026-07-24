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
