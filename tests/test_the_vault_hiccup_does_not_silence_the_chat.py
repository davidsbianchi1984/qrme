"""The vault hiccup that must not silence the chat.

The field report: chat stopped working right after a social page was
fetched and sealed. The fetch was the first thing to give the profile a
PDI-sealed source item, and the chat route resolves every sealed item on
every turn — through a client that raises on any vault error. One erroring
record, and every conversation with the profile answered 500.

A profile whose vault is momentarily unreachable should simply not recall
that material this turn — degraded memory, not a dead voice.
"""

import json

from qrme import db


class _FlakyVault:
    """Seals fine, then fails every readback — the beta's bad afternoon."""

    def __init__(self):
        self.sealed = {}

    def put(self, key, value):
        self.sealed[key] = value

    def get(self, key):
        raise RuntimeError("PDI get failed: 503")


def _seal_item(profile_id, vault):
    item_id = db.new_id("src")
    key = f"qrme/{profile_id}/sources/{item_id}"
    vault.put(key, json.dumps({"content": "Gardener. Tomatoes."}))
    conn = db.connect()
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, created_at) VALUES (?,?,'social_post',?,NULL,?,?)",
        (item_id, profile_id, "instagram · Dana", key, db.utcnow()),
    )
    conn.commit()


def test_chat_answers_even_when_the_vault_does_not(client, profile_id,
                                                   interactor_id):
    vault = _FlakyVault()
    client.app.state.pdi = vault
    try:
        _seal_item(profile_id, vault)
        r = client.post(f"/profiles/{profile_id}/chat", json={
            "interactor_id": interactor_id, "message": "Hello!",
        })
        assert r.status_code == 200, r.text
        assert r.json()["profile_message"]["content"]
    finally:
        client.app.state.pdi = None


def test_the_unreadable_item_resolves_to_nothing_not_an_error(client,
                                                              profile_id):
    from qrme.common import source_items
    vault = _FlakyVault()
    _seal_item(profile_id, vault)
    items = source_items(profile_id, vault)
    sealed = next(i for i in items if i["pdi_key"])
    assert sealed["content"] is None
