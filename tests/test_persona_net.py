"""The persona network (claims 22 and 26): attention layers conditioned on
the degree of engagement, trained offline on encrypted weights, on every
path a profile speaks — a chat reply, a hired seat, a room turn, the Agent.

    asked     condition the inference using attention layers based on the
              degree of engagement; fine-tune the model offline, encrypted
    mattered  the attention is QRME's own (numpy forward and backward,
              gradient-checked here), the conditioning is a printed number
              on every reply, and the training never leaves the host
"""

from __future__ import annotations

import numpy as np
import pytest

from qrme import authoring, db, persona, persona_net as pn
from tests.test_a_company_is_hired_one_interview_at_a_time import (
    _found, _hire, _seat)
from tests.test_capabilities import as_owner, make_interactor, make_profile

TURNS = ["hello there, how are you today?",
         "I feel so tired and worried lately, everything is hard",
         "Thanks! that was lovely of you to say",
         "ok",
         "Tell me about the old garden again please, I loved that story"]


# -- the network itself -------------------------------------------------------

def test_every_gradient_matches_finite_differences():
    """Hand-written backward, checked parameter by parameter."""
    p = pn.init_params(3)
    eng = pn.replay_engagement(TURNS)
    X, e, tau = pn.features(TURNS, eng), np.array(eng), pn.temperature(eng[-1])
    t_eng, t_emph = 0.4, np.array([0.6, 0.9, 0.3, 0.1])
    g = pn.backward(p, pn.forward(p, X, e, tau), t_eng, t_emph)

    def loss():
        return pn.loss_of(pn.forward(p, X, e, tau), t_eng, t_emph)

    h = 1e-6
    for name in p:
        flat = p[name].reshape(-1)
        # Every scalar of the small tensors; a spread of the big ones.
        for idx in range(0, flat.size, max(1, flat.size // 24)):
            old = flat[idx]
            flat[idx] = old + h
            up = loss()
            flat[idx] = old - h
            down = loss()
            flat[idx] = old
            numeric, analytic = (up - down) / (2 * h), g[name].reshape(-1)[idx]
            assert abs(numeric - analytic) <= 1e-6 + 1e-4 * abs(numeric), (
                name, idx, numeric, analytic)


def test_attention_is_conditioned_by_the_degree_of_engagement():
    """Claim 22, twice over: the per-turn engagement shifts the attention
    logits (gamma), and the current engagement sets the temperature."""
    p = pn.init_params(3)
    eng = np.array(pn.replay_engagement(TURNS))
    X = pn.features(TURNS, eng)
    one_turn_more_engaged = eng.copy()
    one_turn_more_engaged[1] = min(1.0, eng[1] + 0.5)
    a = pn.forward(p, X, eng, 1.0)["layers"][-1]["A"][:, -1, :]
    b = pn.forward(p, X, one_turn_more_engaged, 1.0)["layers"][-1]["A"][:, -1, :]
    assert not np.allclose(a, b)
    # The bias is on the turn whose engagement rose: gamma starts positive,
    # so that key draws more of the row.
    assert b[:, 1].mean() > a[:, 1].mean()
    # A shift shared by every turn cancels in the softmax — the conditioning
    # is on the *relative* degree of engagement across the turns.
    c = pn.forward(p, X, np.clip(eng + 0.2, 0, 1), 1.0)["layers"][-1]["A"][:, -1, :]
    assert np.allclose(a, c)

    sharp = pn.forward(p, X, eng, pn.temperature(0.95))["layers"][-1]["A"][:, -1, :]
    wide = pn.forward(p, X, eng, pn.temperature(0.05))["layers"][-1]["A"][:, -1, :]
    # A lower temperature concentrates the row: its maximum rises.
    assert sharp.max(axis=1).mean() > wide.max(axis=1).mean()
    assert pn.temperature(0.95) < pn.temperature(0.05)

    engaged = pn.condition("prof_t", TURNS, engagement=0.95)
    drifting = pn.condition("prof_t", TURNS, engagement=0.05)
    assert engaged["temperature"] < drifting["temperature"]
    assert ([a["weight"] for a in engaged["attention"]]
            != [a["weight"] for a in drifting["attention"]])
    assert set(engaged["emphases"]) == set(pn.EMPHASES)


def test_the_weights_are_ciphertext_and_bound_to_their_profile(monkeypatch, tmp_path):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "w.db"))
    p = pn.init_params(1)
    blob = pn.seal("prof_a", p)
    assert b'"names"' not in blob and b"W_in" not in blob
    back = pn.unseal("prof_a", blob)
    assert all(np.array_equal(p[k], back[k]) for k in p)
    from cryptography.exceptions import InvalidTag
    with pytest.raises(InvalidTag):
        pn.unseal("prof_b", blob)          # another profile's row
    monkeypatch.setenv("QRME_MODEL_KEY", "somebody-else's-deployment")
    with pytest.raises(InvalidTag):
        pn.unseal("prof_a", blob)          # another deployment's key


# -- on the product's doors ---------------------------------------------------

def _talk(client, pid, user, n=4):
    for i in range(n):
        r = client.post(f"/profiles/{pid}/chat", json={
            "interactor_id": user, "message": TURNS[i % len(TURNS)]})
        assert r.status_code == 200, r.text


def test_a_chat_reply_is_conditioned_and_says_so(client):
    p = make_profile(client)
    user = make_interactor(client)
    _talk(client, p["id"], user, 3)
    status = client.get(f"/profiles/{p['id']}/persona-net").json()
    assert status["trained"] is False and status["version"] == 0
    assert status["encrypted_at_rest"] is True
    assert status["external_transmission"] is False
    rows = [r for r in status["recent"] if r["surface"] == "reply"]
    assert rows and rows[0]["interactor_id"] == user
    # The third reply attended over the three turns before it, by quote.
    assert [a["quote"][:20] for a in rows[0]["attention"]] == [
        t[:20] for t in TURNS[:3]]
    assert set(rows[0]["emphases"]) == set(pn.EMPHASES)
    assert 0.5 <= rows[0]["temperature"] <= 1.5


def test_the_prompt_carries_the_block_on_every_speaking_path(client):
    """The one builder every surface uses appends it — so a room turn or a
    letter with no interactor is conditioned on the profile's recent turns,
    and recorded as such."""
    p = make_profile(client)
    user = make_interactor(client)
    _talk(client, p["id"], user, 2)
    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (p["id"],)).fetchone())
    prompt = persona.build_system_prompt(profile, None, None, among=[])
    assert "Engagement-conditioned attention" in prompt
    assert "Weight your focus accordingly" in prompt
    row = db.connect().execute(
        "SELECT surface, interactor_id FROM persona_conditioning"
        " WHERE profile_id=? ORDER BY rowid DESC LIMIT 1", (p["id"],)).fetchone()
    assert row["surface"] == "room" and row["interactor_id"] is None


def test_a_hired_seat_is_conditioned_like_any_profile(client):
    """A job/position profile is a profile: the seat June was hired into
    speaks through the same builder and leaves the same record."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    hired = _hire(client, me, co, seat)
    as_owner(client, me)
    user = make_interactor(client, "Customer")
    _talk(client, hired["profile_id"], user, 2)
    recent = pn.conditioning_of(hired["profile_id"])
    assert recent and recent[0]["surface"] == "reply"
    assert recent[0]["interactor_id"] == user
    assert recent[0]["attention"][0]["quote"].startswith(TURNS[0][:20])
    # And the seat's weights train on its own customers' history like any
    # profile's, sealed the same way.
    net = pn.train(hired["profile_id"])
    assert net["trained"] is True and net["loss_after"] < net["loss_before"]


def test_the_agent_is_conditioned_on_its_owners_turns(client):
    p = make_profile(client)

    class Capture:
        system = None

        def generate(self, system, messages):
            Capture.system = system
            return "done."

    history = [{"role": "user", "content": TURNS[0]},
               {"role": "assistant", "content": "hello"},
               {"role": "user", "content": TURNS[1]}]
    authoring.converse("make the header blue", history, app=client.app,
                       profile_id=p["id"], authorization=None,
                       provider=Capture())
    assert "Engagement-conditioned attention" in Capture.system
    assert "attends most to" in Capture.system
    row = db.connect().execute(
        "SELECT surface, attention FROM persona_conditioning"
        " WHERE profile_id=? ORDER BY rowid DESC LIMIT 1", (p["id"],)).fetchone()
    assert row["surface"] == "agent"
    assert "make the header blue" in row["attention"]


# -- fine-tuning (claim 26) --------------------------------------------------

def test_finetune_trains_the_attention_weights_offline(client, monkeypatch):
    monkeypatch.setenv("QRME_OFFLINE", "1")
    p = make_profile(client)
    user = make_interactor(client)
    _talk(client, p["id"], user, 5)
    before = pn.load(p["id"])[0]

    ft = client.post(f"/profiles/{p['id']}/finetune")
    assert ft.status_code == 201, ft.text
    ft = ft.json()
    assert ft["offline_mode"] is True and ft["external_transmission"] is False
    net = ft["network"]
    assert net["trained"] is True and net["samples"] == 4 and net["steps"] > 0
    assert net["loss_after"] < net["loss_before"]
    assert net["encrypted_at_rest"] is True and net["version"] == 1

    after, version = pn.load(p["id"])
    assert version == 1
    assert any(not np.array_equal(before[k], after[k]) for k in before)
    # At rest the row is ciphertext; the layout header never appears.
    blob = db.connect().execute(
        "SELECT blob FROM persona_weights WHERE profile_id=?",
        (p["id"],)).fetchone()["blob"]
    assert b'"names"' not in bytes(blob)

    # The next reply is conditioned by the trained weights, and says so.
    _talk(client, p["id"], user, 1)
    status = client.get(f"/profiles/{p['id']}/persona-net").json()
    assert status["trained"] is True and status["loss_after"] < status["loss_before"]
    assert status["recent"][0]["weights_version"] == 1

    # Training again versions the artifact rather than replacing history.
    assert client.post(f"/profiles/{p['id']}/finetune").json()["network"]["version"] == 2


def test_finetune_without_two_turns_says_why_it_did_not_train(client):
    p = make_profile(client)
    user = make_interactor(client)
    _talk(client, p["id"], user, 1)
    net = client.post(f"/profiles/{p['id']}/finetune").json()["network"]
    assert net["trained"] is False and net["steps"] == 0
    assert "two approved turns" in net["reason"]


def test_erasing_the_profile_takes_the_weights_and_the_record(client):
    p = make_profile(client)
    user = make_interactor(client)
    _talk(client, p["id"], user, 3)
    client.post(f"/profiles/{p['id']}/finetune")
    conn = db.connect()
    assert conn.execute("SELECT COUNT(*) FROM persona_weights WHERE profile_id=?",
                        (p["id"],)).fetchone()[0] == 1
    r = client.delete(f"/profiles/{p['id']}")
    assert r.status_code in (200, 204), r.text
    for table in ("persona_weights", "persona_conditioning"):
        assert conn.execute(f"SELECT COUNT(*) FROM {table} WHERE profile_id=?",
                            (p["id"],)).fetchone()[0] == 0
