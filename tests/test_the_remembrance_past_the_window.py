"""The remembrance past the window.

Chat context is the last thirty approved turns. The thirty-first-oldest did
not fade — it vanished: nothing that fell off the window could reach a
prompt again. These tests hold the fold that fixes it: aged-out turns are
distilled — by the profile's own provider — into one running paragraph per
(profile, interactor) that rides every prompt, is readable at its own door
by the two people it is of, and dies with the memory it belongs to.
"""

from qrme import db, llm, remembrance
from qrme.routers import interaction


class _Distiller:
    """Replies to chat, and answers the distiller with a known paragraph."""

    def __init__(self):
        self.system = None
        self.folds = 0

    def generate(self, system, messages):
        if "long memory" in system:
            self.folds += 1
            return "They planted tomatoes in spring and worry about frost."
        self.system = system
        return "a reply"


def _wire(monkeypatch):
    provider = _Distiller()
    monkeypatch.setattr(llm, "provider_for_profile",
                        lambda *a, **kw: provider)
    return provider


def _fill(profile_id, interactor_id, n):
    """Approved turns straight into the table — the fold reads, not relives."""
    conn = db.connect()
    for i in range(n):
        conn.execute(
            "INSERT INTO messages (id, profile_id, interactor_id, role,"
            " content, status, created_at) VALUES (?,?,?,?,?,?,?)",
            (db.new_id("msg"), profile_id, interactor_id,
             "interactor" if i % 2 == 0 else "profile",
             f"turn {i}", "approved", f"2026-01-01T00:{i:02d}:00Z"),
        )
    conn.commit()


def test_under_the_window_nothing_is_folded(client, profile_id,
                                            interactor_id, monkeypatch):
    provider = _wire(monkeypatch)
    _fill(profile_id, interactor_id, 5)
    r = client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id, "message": "hello"})
    assert r.status_code == 200, r.text
    assert provider.folds == 0
    assert remembrance.get(profile_id, interactor_id) is None


def test_aged_out_turns_become_the_remembrance_in_the_prompt(
        client, profile_id, interactor_id, monkeypatch):
    provider = _wire(monkeypatch)
    extra = 6  # turns beyond the window — what the fold must cover
    _fill(profile_id, interactor_id, interaction.MEMORY_WINDOW + extra)
    r = client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id, "message": "hello again"})
    assert r.status_code == 200, r.text
    assert provider.folds == 1
    assert "planted tomatoes" in provider.system
    assert "earlier conversations" in provider.system

    row = remembrance.get(profile_id, interactor_id)
    assert row["covers"] >= extra
    # The next turn folds only what newly aged out — not everything again.
    covers_before = row["covers"]
    client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id, "message": "and again"})
    assert remembrance.get(profile_id, interactor_id)["covers"] >= covers_before


def test_the_remembrance_has_its_own_door(client, profile_id,
                                          interactor_id, monkeypatch):
    _wire(monkeypatch)
    extra = 4  # turns beyond the window — what the fold must cover
    _fill(profile_id, interactor_id, interaction.MEMORY_WINDOW + extra)
    client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id, "message": "hello"})
    out = client.get(
        f"/profiles/{profile_id}/memory/{interactor_id}/remembrance").json()
    assert "planted tomatoes" in out["content"]
    assert out["covers"] >= extra
    assert out["updated_at"]


def test_before_any_fold_the_door_answers_empty(client, profile_id,
                                                interactor_id):
    out = client.get(
        f"/profiles/{profile_id}/memory/{interactor_id}/remembrance").json()
    assert out == {"content": None, "covers": 0, "updated_at": None}


def test_erasing_memory_erases_the_remembrance(client, profile_id,
                                               interactor_id, monkeypatch):
    _wire(monkeypatch)
    _fill(profile_id, interactor_id, interaction.MEMORY_WINDOW + 4)
    client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id, "message": "hello"})
    assert remembrance.get(profile_id, interactor_id) is not None
    assert client.delete(
        f"/profiles/{profile_id}/memory/{interactor_id}").status_code == 204
    assert remembrance.get(profile_id, interactor_id) is None
    out = client.get(
        f"/profiles/{profile_id}/memory/{interactor_id}/remembrance").json()
    assert out["content"] is None


def test_a_distiller_failure_never_breaks_the_reply(client, profile_id,
                                                    interactor_id,
                                                    monkeypatch):
    class Flaky:
        def generate(self, system, messages):
            if "long memory" in system:
                raise RuntimeError("provider down mid-fold")
            return "a reply"
    monkeypatch.setattr(llm, "provider_for_profile",
                        lambda *a, **kw: Flaky())
    _fill(profile_id, interactor_id, interaction.MEMORY_WINDOW + 4)
    r = client.post(f"/profiles/{profile_id}/chat", json={
        "interactor_id": interactor_id, "message": "hello"})
    assert r.status_code == 200, r.text
    assert r.json()["profile_message"]["content"] == "a reply"
    assert remembrance.get(profile_id, interactor_id) is None
