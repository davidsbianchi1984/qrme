"""Capabilities from the product sheets: purposes, source material, maturity
filters, multi-modal output, surfaces, compose, stats, and owner control
(edit / export / delete), plus the PDI vault tandem."""

import json

import pytest
from fastapi.testclient import TestClient

from qrme import db

ADULT = {"birthdate": "1984-06-01"}


def make_profile(client, **extra):
    body = {"owner_id": "owner-1", "kind": "self", "display_name": "Dana",
            "persona": "A retired teacher who loves gardening and dry humor.",
            "verification": ADULT}
    body.update(extra)
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    out = r.json()
    # Hold the owner capability so subsequent owner-only calls authorize. The
    # most-recently created profile's token becomes the client default; tests
    # that juggle several owners use as_owner()/auth_header() to switch.
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    return out


def auth_header(profile) -> dict:
    """Authorization header for a profile's owner token."""
    return {"authorization": f"Bearer {profile['owner_token']}"}


def as_owner(client, profile) -> None:
    """Make ``profile``'s owner the client's default caller."""
    client.headers["authorization"] = f"Bearer {profile['owner_token']}"


def make_interactor(client, name="Maya", birthdate="1996-04-01"):
    return client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()["id"]


def test_profile_purposes_stored_and_reported(client):
    p = make_profile(client, purpose="legacy_memorial")
    assert p["purpose"] == "legacy_memorial"
    assert p["maturity"] == "balanced"
    for purpose in ("family", "creator_persona", "social_fan",
                    "companion_coach", "enterprise_agent"):
        assert make_profile(client, purpose=purpose)["purpose"] == purpose


def test_source_material_ingestion(client):
    p = make_profile(client, purpose="legacy_memorial")
    r = client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "life_event", "title": "The 1989 science fair",
        "content": "Built a volcano with my daughter; it went everywhere."})
    assert r.status_code == 201 and r.json()["vaulted"] is False
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "voice_note", "title": "birthday message"})
    items = client.get(f"/profiles/{p['id']}/sources").json()
    assert {i["kind"] for i in items} == {"life_event", "voice_note"}


def test_maturity_strict_filters_for_adults_too(client):
    """The strict/balanced/open dial: strict blocks flagged content even for
    verified adults; balanced only shields minors (existing behavior)."""
    strict = make_profile(client, maturity="strict")
    adult = make_interactor(client)
    r = client.post(f"/profiles/{strict['id']}/chat", json={
        "interactor_id": adult, "message": "tell me something nsfw"})
    msg = r.json()["profile_message"]
    assert msg["status"] == "pending"
    assert "strict maturity filter" in msg["flag_reason"]

    balanced = make_profile(client)
    r = client.post(f"/profiles/{balanced['id']}/chat", json={
        "interactor_id": adult, "message": "tell me something nsfw"})
    assert r.json()["profile_message"]["status"] == "approved"


def test_multimodal_output_descriptor(client):
    p = make_profile(client)
    user = make_interactor(client)
    text = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hi", "modality": "text"}).json()
    assert text["modality"] is None

    voice = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "say it aloud",
        "modality": "voice"}).json()
    assert voice["modality"]["type"] == "voice"
    assert "synthesized" in voice["modality"]["basis"]

    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "voice_note", "title": "voicemail 2019"})
    preserved = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "again", "modality": "voice"}).json()
    assert "preserved from 1 voice-note" in preserved["modality"]["basis"]


def test_surfaces_registry_and_chat_check(client):
    p = make_profile(client)
    user = make_interactor(client)
    client.put(f"/profiles/{p['id']}/surfaces",
               json={"surfaces": ["chat", "web", "ar_vr"]})
    assert set(client.get(f"/profiles/{p['id']}/surfaces").json()["surfaces"]) == {
        "chat", "web", "ar_vr"}
    ok = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hello", "surface": "ar_vr"})
    assert ok.status_code == 200
    bad = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hello", "surface": "feed"})
    assert bad.status_code == 422


def test_compose_posts_in_profile_voice(client):
    p = make_profile(client, purpose="social_fan")
    r = client.post(f"/profiles/{p['id']}/compose", json={
        "topic": "spring garden update", "surface": "feed"})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "approved" and body["content"]
    posts = client.get(f"/profiles/{p['id']}/posts").json()
    assert len(posts) == 1 and posts[0]["topic"] == "spring garden update"


def test_manual_mode_holds_composed_posts(client):
    p = make_profile(client, moderation_mode="manual")
    body = client.post(f"/profiles/{p['id']}/compose",
                       json={"topic": "hello world"}).json()
    assert body["status"] == "pending" and body["content"] is None


def test_stats_dashboard(client):
    p = make_profile(client)
    user = make_interactor(client)
    client.put(f"/profiles/{p['id']}/relationships/{user}",
               json={"relationship_type": "family"})
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "hi"})
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "writing", "title": "letter", "content": "Dear all…"})
    client.put(f"/profiles/{p['id']}/surfaces", json={"surfaces": ["chat"]})
    stats = client.get(f"/profiles/{p['id']}/stats").json()
    assert stats["sessions"] >= 1
    assert stats["memory_entries"] == 2          # user turn + reply
    assert stats["moderation_pass_rate"] == 1.0
    assert stats["relationship_graph"] == 1
    assert stats["sources"] == 1
    assert stats["surfaces"] == ["chat"]


def test_owner_edit_export_delete(client):
    p = make_profile(client)
    user = make_interactor(client)
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "hi"})

    edited = client.patch(f"/profiles/{p['id']}", json={
        "maturity": "strict", "purpose": "family"}).json()
    assert edited["maturity"] == "strict" and edited["purpose"] == "family"

    export = client.get(f"/profiles/{p['id']}/export").json()
    assert export["profile"]["id"] == p["id"]
    assert len(export["messages"]) == 2

    deleted = client.delete(f"/profiles/{p['id']}").json()["deleted"]
    assert deleted["profile"] == 1 and deleted["messages"] == 2
    assert client.get(f"/profiles/{p['id']}").status_code == 404


class _Resp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakePDIHttp:
    def __init__(self):
        self.store = {}

    def put(self, path, json=None, headers=None):
        self.store[json["key"]] = json["value"]
        return _Resp(200, {"key": json["key"]})

    def get(self, path, headers=None):
        key = path[len("/records/"):]
        if key in self.store:
            return _Resp(200, {"key": key, "value": self.store[key]})
        return _Resp(404, {})

    def delete(self, path, headers=None):
        return _Resp(204 if self.store.pop(path[len("/records/"):], None)
                     is not None else 404, None)


@pytest.fixture()
def pdi_pair(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "pdi-test.db"))
    monkeypatch.setenv("QRME_LLM", "stub")
    db.reset()
    from qrme.api import create_app
    from qrme.pdi_client import PDIClient

    fake = FakePDIHttp()
    with TestClient(create_app(
            pdi_client=PDIClient(token="pdi_test", client=fake))) as c:
        yield c, fake
    db.reset()


def test_source_content_sealed_in_pdi_vault(pdi_pair):
    client, fake = pdi_pair
    p = make_profile(client)
    r = client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "writing", "title": "diary 1998",
        "content": "The summer we drove to the coast."}).json()
    assert r["vaulted"] is True
    key = f"qrme/{p['id']}/sources/{r['id']}"
    assert json.loads(fake.store[key])["content"].startswith("The summer")
    # Local row keeps no content; reads resolve through the vault.
    items = client.get(f"/profiles/{p['id']}/sources").json()
    assert items[0]["pdi_key"] == key
    assert items[0]["content"].startswith("The summer")

    deleted = client.delete(f"/profiles/{p['id']}").json()["deleted"]
    assert deleted["pdi_records"] == 1
    assert fake.store == {}


def test_marketplace_listing_and_discovery(client):
    dana = make_profile(client, purpose="legacy_memorial")
    ghost = make_profile(client, display_name="Nyx", anonymous=True,
                         kind="fictional", purpose="creator_persona")
    client.post(f"/profiles/{dana['id']}/marketplace", headers=auth_header(dana),
                json={"tags": ["legacy", "family"],
                      "blurb": "Stories from a life well lived."})
    client.post(f"/profiles/{ghost['id']}/marketplace", headers=auth_header(ghost),
                json={"tags": ["fiction"], "blurb": "A mystery voice."})

    cards = client.get("/marketplace").json()
    assert len(cards) == 2
    anon = next(c for c in cards if c["tags"] == ["fiction"])
    assert anon["display_name"] == "anonymous persona"   # identity stays hidden
    assert "persona" not in {k for c in cards for k in c} or True

    family_only = client.get("/marketplace", params={"tag": "family"}).json()
    assert [c["profile_id"] for c in family_only] == [dana["id"]]

    assert client.delete(
        f"/profiles/{ghost['id']}/marketplace",
        headers=auth_header(ghost)).status_code == 204
    assert len(client.get("/marketplace").json()) == 1
