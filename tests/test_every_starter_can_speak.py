"""Every starter in the pack can speak, and nobody's own choice is touched.

The field report asked for the collection decorated: portraits, and voices
from the owner's own engine account. The portraits landed rounds ago; this
holds the voices — bound at seed and repaired at startup exactly the way
the faces are, as references that cost nothing until somebody asks a
profile to speak on a host that holds the engine key.
"""

from __future__ import annotations

from qrme import db, seed, spoken


def test_every_starter_voice_names_a_real_starter():
    """The map's keys are handles the seed actually plants — a voice bound
    to a typo would report success and decorate nobody."""
    handles = {h for h, *_ in seed.STARTERS + seed.RATED}
    handles |= {seed.FOUNDER_HANDLE, seed.VERIFIED_HANDLE}
    stray = sorted(set(seed.STARTER_VOICES) - handles)
    assert not stray, f"voices for handles the seed never plants: {stray}"


def test_seeding_binds_the_voices(client):
    client.post("/marketplace/seed", json={})
    conn = db.connect()
    row = conn.execute(
        "SELECT h.profile_id FROM handles h WHERE h.handle='dr_amara_osei'"
    ).fetchone()
    assert row, "the starter itself did not seed"
    binding = spoken.bound(row["profile_id"])
    assert binding["speaks"], "the starter seeded with no voice bound"
    assert binding["provider"] == "elevenlabs"
    assert binding["voice_id"] == seed.STARTER_VOICES["dr_amara_osei"][0]


def test_the_founders_speak_with_the_owners_clone(client):
    client.post("/marketplace/seed", json={})
    conn = db.connect()
    for handle in (seed.FOUNDER_HANDLE, seed.VERIFIED_HANDLE):
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()
        if row is None:
            continue
        binding = spoken.bound(row["profile_id"])
        assert binding["voice_id"] == seed.STARTER_VOICES[handle][0], handle


def test_a_bound_voice_is_never_overwritten(client):
    """Repair, not reset — the same promise the portrait backfill keeps."""
    client.post("/marketplace/seed", json={})
    conn = db.connect()
    row = conn.execute(
        "SELECT profile_id FROM handles WHERE handle='marcus_bell'").fetchone()
    pid = row["profile_id"]
    spoken.bind(pid, "elevenlabs", "v-owners-own", "Mine")
    client.post("/marketplace/seed", json={})
    seed.repair()
    assert spoken.bound(pid)["voice_id"] == "v-owners-own", (
        "the repair overwrote a binding an owner made")
