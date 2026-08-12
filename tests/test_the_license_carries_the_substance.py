"""A derived agent receives the expertise the buyer paid for — and a manifest.

The amended claims draw the line this file walks: parameter-level substance
travels ("latent embeddings that maintain cross-session state ... without
storing raw user data"), raw material does not. A finetune derive carries the
profile's own knowledge items and its characteristics; a clone additionally
carries an aggregate adaptation summary. Interactor messages and
per-relationship embeddings, the person's voice, vaulted content and
marketplace pack items never cross — and the manifest written at derive time
says so, to both parties.
"""

import json

from qrme import db
from tests.test_capabilities import as_owner, make_profile


def _buyer(client, birthdate="1990-01-01"):
    who = client.post("/interactors", json={
        "display_name": "Buyer", "birthdate": birthdate}).json()
    return who["id"], {"authorization": f"Bearer {who['token']}"}


def _license_and_buy(client, p, kind):
    as_owner(client, p)
    client.put(f"/profiles/{p['id']}/license", json={"kind": kind, "price": 20})
    buyer_id, hdr = _buyer(client)
    g = client.post(f"/profiles/{p['id']}/license/acquire", headers=hdr).json()
    return buyer_id, hdr, g


def test_a_finetune_carries_knowledge_and_characteristics(client):
    p = make_profile(client, persona="A master luthier's craft.")
    as_owner(client, p)
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "knowledge", "title": "tonewood",
        "content": "Spruce tops want stiffness along the grain."})
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "writing", "title": "bracing notes",
        "content": "Scalloped bracing loosens the low end."})
    client.put(f"/profiles/{p['id']}/steering",
               json={"values": {"warmth": 80, "verbosity": 30}})

    buyer_id, hdr, g = _license_and_buy(client, p, "finetune")
    derived = client.post(
        f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
        headers=hdr).json()

    manifest = derived["manifest"]
    assert manifest["carried"]["knowledge_items"] == 2
    assert manifest["carried"]["steering_dials"] >= 2

    # The knowledge is really on the child, not just counted in a receipt.
    mine = {"authorization": f"Bearer {derived['owner_token']}"}
    child_id = derived["derived_profile_id"]
    sources = client.get(f"/profiles/{child_id}/sources", headers=mine).json()
    titles = {s["title"] for s in sources}
    assert {"tonewood", "bracing notes"} <= titles
    dials = client.get(f"/profiles/{child_id}/steering", headers=mine).json()
    assert dials["values"]["warmth"] == 80

    # A finetune does not carry the adaptation summary — the manifest says so.
    assert "adaptation_summary" not in manifest["carried"]
    assert any(w["item"] == "adaptation summary" for w in manifest["withheld"])


def test_a_clone_adds_the_aggregate_adaptation_summary(client):
    p = make_profile(client, persona="A calm CBT therapist's approach.")
    # Two relationships condition the source before the sale.
    ids = []
    for name in ("Ana", "Ben"):
        who = client.post("/interactors",
                          json={"display_name": name}).json()["id"]
        r = client.post(f"/profiles/{p['id']}/chat",
                        json={"interactor_id": who, "message": "hello there"})
        assert r.status_code == 200
        ids.append(who)

    buyer_id, hdr, g = _license_and_buy(client, p, "clone")
    derived = client.post(
        f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
        headers=hdr).json()

    summary = derived["manifest"]["carried"]["adaptation_summary"]
    assert summary["relationships_aggregated"] == 2
    assert "engagement" in summary["disposition"]
    # Aggregate only: no interactor appears anywhere in what traveled.
    flat = json.dumps(derived["manifest"])
    for interactor in ids:
        assert interactor not in flat

    # The summary rides the child as a knowledge item, so it conditions the
    # derived agent the same way any source does.
    mine = {"authorization": f"Bearer {derived['owner_token']}"}
    sources = client.get(f"/profiles/{derived['derived_profile_id']}/sources",
                         headers=mine).json()
    assert any(s["title"] == "licensed adaptation summary" for s in sources)


def test_raw_interactor_data_never_travels(client):
    p = make_profile(client)
    who = client.post("/interactors", json={"display_name": "Cara"}).json()["id"]
    assert client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": who,
        "message": "my private worry about work"}).status_code == 200

    buyer_id, hdr, g = _license_and_buy(client, p, "clone")
    derived = client.post(
        f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
        headers=hdr).json()
    child_id = derived["derived_profile_id"]

    conn = db.connect()
    assert conn.execute("SELECT COUNT(*) AS n FROM messages WHERE profile_id=?",
                        (child_id,)).fetchone()["n"] == 0
    assert conn.execute(
        "SELECT COUNT(*) AS n FROM persona_embeddings WHERE profile_id=?",
        (child_id,)).fetchone()["n"] == 0
    # And the message content itself is nowhere in what was handed over.
    for s in conn.execute("SELECT content FROM source_items WHERE profile_id=?",
                          (child_id,)).fetchall():
        assert "private worry" not in (s["content"] or "")
    assert any("raw interactor data never travels" in w["reason"]
               for w in derived["manifest"]["withheld"])


def test_vaulted_and_pack_content_stay_behind(client):
    p = make_profile(client)
    as_owner(client, p)
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "knowledge", "title": "open note", "content": "travels"})
    conn = db.connect()
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, created_at) VALUES (?,?,?,?,NULL,?,?)",
        (db.new_id("src"), p["id"], "knowledge", "sealed note",
         f"qrme/{p['id']}/sources/sealed", db.utcnow()))
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,?,?)",
        (db.new_id("src"), p["id"], "knowledge", "pack lesson",
         "belongs to the pack author", "pck_x", db.utcnow()))
    conn.commit()

    buyer_id, hdr, g = _license_and_buy(client, p, "finetune")
    derived = client.post(
        f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
        headers=hdr).json()

    manifest = derived["manifest"]
    assert manifest["carried"]["knowledge_items"] == 1
    reasons = " · ".join(w["reason"] for w in manifest["withheld"])
    assert "vault" in reasons and "pack" in reasons

    mine = {"authorization": f"Bearer {derived['owner_token']}"}
    titles = {s["title"] for s in client.get(
        f"/profiles/{derived['derived_profile_id']}/sources",
        headers=mine).json()}
    assert "sealed note" not in titles and "pack lesson" not in titles


def test_the_voice_is_withheld_by_name(client):
    p = make_profile(client)
    as_owner(client, p)
    assert client.put(f"/profiles/{p['id']}/voiceprint/consent", json={
        "own_voice": True, "sources": ["direct"]}).status_code == 200

    buyer_id, hdr, g = _license_and_buy(client, p, "clone")
    derived = client.post(
        f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
        headers=hdr).json()
    voice = [w for w in derived["manifest"]["withheld"]
             if w["item"] == "voice print"]
    assert voice and "biometric" in voice[0]["reason"]
    # And no voice rows exist for the child.
    conn = db.connect()
    assert conn.execute(
        "SELECT COUNT(*) AS n FROM voice_consents WHERE profile_id=?",
        (derived["derived_profile_id"],)).fetchone()["n"] == 0


def test_the_owner_reads_the_manifest_on_their_grant(client):
    p = make_profile(client)
    as_owner(client, p)
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "knowledge", "title": "one", "content": "item"})
    buyer_id, hdr, g = _license_and_buy(client, p, "finetune")
    client.post(f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
                headers=hdr)

    as_owner(client, p)
    grants = client.get(f"/profiles/{p['id']}/licenses").json()
    assert grants[0]["manifest"]["carried"]["knowledge_items"] == 1
    # An undelivered grant carries no manifest — nothing has crossed yet.
    buyer2, hdr2 = _buyer(client)
    client.post(f"/profiles/{p['id']}/license/acquire", headers=hdr2)
    grants = client.get(f"/profiles/{p['id']}/licenses").json()
    assert grants[1]["manifest"] is None
