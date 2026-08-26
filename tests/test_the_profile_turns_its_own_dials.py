"""The profile turns its own dials, when the person asks it to.

Field direction: *"if the user asked the synthetic profile to be more
funny, it will come up with steady intervals maybe like +25 or -25...
goes up to 100... user shouldn't have to go and navigate to that button
— +/- 25 intervals or max or none or on/off for all of them."*

The rail put the dials beside the face, but the rail is the owner's
hand. The person actually talking can now just ask: the move rides the
reply the way a document does (qrme/composing.py), through the same
`steering.set_dials` the sliders write — same clamps, same intimacy
rule, and the same lock, whose own docstring anticipated this feature:
while it stands, any automation is refused.
"""

from __future__ import annotations

from qrme import selfsteer, steering

from tests.test_a_profile_hands_something_over import Composing  # noqa: F401
from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile)
from tests.test_the_profile_remembers_by_meaning import _chat


class Turning:
    """A provider that answers with a dial move, as the guidance asks."""

    def __init__(self, marker="[[dial: humor +25]]",
                 said="Alright — funnier it is."):
        self.marker, self.said = marker, said
        self.prompts: list[str] = []

    def generate(self, system, messages):
        self.prompts.append(system)
        return f"{self.said}\n{self.marker}"


# -- the grammar -------------------------------------------------------------

def test_the_four_moves_and_nothing_else():
    spoken, moves = selfsteer.split(
        "Done.\n[[dial: humor +25]]\n[[dial: warmth -25]]\n"
        "[[dial: mood max]]\n[[dial: verbosity none]]")
    assert spoken == "Done."
    assert moves == {"humor": "+25", "warmth": "-25",
                     "mood": "max", "verbosity": "none"}


def test_a_malformed_marker_is_stripped_and_moves_nothing():
    """A person never reads a marker (the composing lesson), and a model
    inventing +90 does not get a bigger step for the enthusiasm."""
    spoken, moves = selfsteer.split("Sure. [[dial: humor +90]]")
    assert "[[" not in spoken
    assert moves == {}


def test_all_fans_out_to_every_dial(client):
    profile = make_profile(client)
    assert selfsteer.apply(profile["id"], {"all": "none"}, adult=False)
    assert set(steering.get(profile["id"]).values()) == {0}
    assert selfsteer.apply(profile["id"], {"all": "+25"}, adult=False)
    assert steering.get(profile["id"])["humor"] == 25


def test_the_step_is_steady_and_the_ends_hold(client):
    profile = make_profile(client)
    for want in (75, 100, 100):
        assert selfsteer.apply(profile["id"], {"humor": "+25"}, adult=False)
        assert steering.get(profile["id"])["humor"] == want, (
            "the step is not the steady 25 the owner named")


def test_intimacy_never_rises_on_a_non_adult_profile(client):
    profile = make_profile(client)
    selfsteer.apply(profile["id"], {"intimacy": "max"}, adult=False)
    assert steering.get(profile["id"])["intimacy"] == 0, (
        "the conversational path raised the one dial set_dials hard-clamps")


# -- the whole way through ---------------------------------------------------

def test_be_more_funny_moves_the_dial(client, profile_id, interactor_id,
                                      monkeypatch):
    from qrme import llm
    made = Turning()
    monkeypatch.setattr(llm, "provider_for_profile", lambda *a, **k: made)
    out = _chat(client, profile_id, interactor_id, "be more funny")
    turn = out["profile_message"]
    assert "[[" not in (turn["content"] or ""), (
        "the marker landed in the bubble")
    assert steering.get(profile_id)["humor"] == 75, (
        "the person asked, the profile promised, and no dial moved")
    assert "[[dial:" in made.prompts[0], (
        "the prompt never teaches the move, so no profile will make it")


def test_the_lock_is_the_owners_veto(client, profile_id, interactor_id,
                                     monkeypatch):
    """steering.lock's own docstring: while the lock holds, every steering
    write — any future automation — is refused. This is that automation."""
    from qrme import llm
    made = Turning()
    monkeypatch.setattr(llm, "provider_for_profile", lambda *a, **k: made)
    steering.lock(profile_id, "the personality nobody can move")
    out = _chat(client, profile_id, interactor_id, "be more funny")
    assert steering.get(profile_id)["humor"] == 50, "the lock did not hold"
    assert "locked" in (out["profile_message"]["content"] or ""), (
        "the change was refused and nobody was told")


def test_a_room_profile_turns_its_dials_too(client, monkeypatch):
    from qrme.routers import community
    made = Turning(marker="[[dial: verbosity -25]]", said="Shorter, then.")
    monkeypatch.setattr(community.llm, "get_provider", lambda *a, **k: made)
    user = make_interactor(client, "Theo", "1990-01-01")
    prof = make_profile(client)
    room = client.post("/rooms", json={
        "topic": "brevity", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": prof["id"]}]}).json()
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"message": "keep it shorter", "sender_id": user})
    turn = r.json()["replies"][0]
    assert "[[" not in (turn["content"] or "")
    assert steering.get(prof["id"])["verbosity"] == 25
