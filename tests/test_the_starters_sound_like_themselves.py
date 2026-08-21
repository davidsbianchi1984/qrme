"""A starter written as a woman speaks with a woman's voice.

The reviewer's call, after listening to the pack: the women in the starter
collection must take a woman's voice from the engine's own list, and the
men a man's — and not the man the sibling guardian product speaks with.
The audit found the collection almost there already, with one systematic
exception: River, the engine's androgynous premade, sat on two men and a
woman. A voice that is deliberately neither reads as the wrong one on a
brief that is deliberately either.

    asked     does each starter have a voice
    mattered  does each starter have their own kind of voice

Two personas whose briefs state no gender (and the coach whose name could
carry either) are left unpinned on purpose: their voices were chosen with
their portraits, and this file refuses to guess what the brief declined
to say.
"""

from __future__ import annotations

from qrme import db, seed, spoken

#: The engine premades the seed draws from, by the gender the engine's own
#: catalogue lists for them. Every non-founder starter voice must be one of
#: these — an id missing here is either a typo or a voice nobody vetted.
VOICES = {
    "XrExE9yKIg1WjnnlVkGX": ("Matilda", "female"),
    "EXAVITQu4vr4xnSDxMaL": ("Sarah", "female"),
    "NP8gGMLAGXx7ddlMa06t": ("Sarika", "female"),
    "Xb7hH8MSUJpSbSDYk0k2": ("Alice", "female"),
    "cgSgspJ2msm6clMCkdW9": ("Jessica", "female"),
    "hpp4J3VqNfWAUOO0d1Us": ("Bella", "female"),
    "FGY2WhTYpPnrIDTdsKH5": ("Laura", "female"),
    "JBFqnCBsd6RMkjVDRZzb": ("George", "male"),
    "cjVigY5qzO86Huf0OWal": ("Eric", "male"),
    "CwhRBWXzGAHq8TQ4Fs17": ("Roger", "male"),
    "IKne3meq5aSn9XLyUdCD": ("Charlie", "male"),
    "bIHbv24MWmeRgasZH58o": ("Will", "male"),
    "TX3LPaxmHKxFdv7VOQHJ": ("Liam", "male"),
    "N2lVS1w4EtoT3dr4eOWO": ("Callum", "male"),
    "pqHfZKP75CvOlQylNhV4": ("Bill", "male"),
    "VZcBEw9QXVSghzV5UKLN": ("Michael Joshua", "male"),
}

#: How each brief presents its persona, read from the briefs and portraits
#: rather than guessed from the name alone. sam_whitfield, wren_okafor and
#: coach_dana_reyes state none and are deliberately absent.
PRESENTATION = {
    "dr_amara_osei": "female", "priya_raman": "female",
    "elena_vasquez": "female", "ingrid_halvorsen": "female",
    "naomi_clarke": "female", "odessa_grant": "female",
    "lucia_moretti": "female", "dr_sana_iqbal": "female",
    "grace_mwangi": "female", "aisha_diallo": "female",
    "rosa_delgado": "female", "cmdr_ellen_park": "female",
    "mimi_beaumont": "female", "nadia_petrova": "female",
    "bev_lindqvist": "female", "dr_lena_whitcomb": "female",
    "dr_priya_nair": "female", "vivienne_sable": "female",
    "marcus_bell": "male", "jonathan_ashe": "male",
    "diego_fuentes": "male", "tomas_rivera": "male",
    "ken_nakamura": "male", "ray_coleman": "male",
    "chef_henri_laurent": "male", "pete_kowalski": "male",
    "dr_felix_baum": "male", "harold_jenkins": "male",
    "jack_osei_turner": "male", "otis_marsh": "male",
    "dr_marcus_adeyemi": "male",
}

#: The voice the sibling guardian product (JIM) speaks with by default —
#: Daniel. The reviewer's second rule: no synthetic profile here borrows
#: the guardian's voice, so the two products never blur into one speaker.
GUARDIANS_VOICE = "onwK4e9ZLuTAKqWW03F9"

FOUNDERS = ("david_bianchi_ai", "david_bianchi")


def test_every_presentation_row_names_a_real_starter():
    stray = sorted(set(PRESENTATION) - set(seed.STARTER_VOICES))
    assert not stray, f"presentation rows for handles with no voice: {stray}"


def test_every_starter_voice_is_a_vetted_premade():
    """Founders aside (the owner's own clone), a starter voice must come
    from the vetted table — which also retires River from the pack: a voice
    that is deliberately neither cannot satisfy a brief that is either."""
    for handle, (voice_id, label) in seed.STARTER_VOICES.items():
        if handle in FOUNDERS:
            continue
        assert voice_id in VOICES, (
            f"{handle} is bound to {label!r} ({voice_id}), which is not in "
            "the vetted premade table")
        assert VOICES[voice_id][0] == label, (
            f"{handle}'s label {label!r} does not name the voice its id "
            f"points at ({VOICES[voice_id][0]})")


def test_a_starter_speaks_with_their_own_kind_of_voice():
    for handle, presented in PRESENTATION.items():
        voice_id, label = seed.STARTER_VOICES[handle]
        assert VOICES[voice_id][1] == presented, (
            f"{handle} presents as {presented} and is bound to {label!r}, "
            f"a {VOICES[voice_id][1]} voice")


def test_no_starter_borrows_the_guardians_voice():
    for handle, (voice_id, label) in seed.STARTER_VOICES.items():
        assert voice_id != GUARDIANS_VOICE, (
            f"{handle} is bound to the guardian product's own default "
            "voice — the two products must not share a speaker")


def test_the_recast_reaches_a_deck_seeded_before_it(client):
    """A deployment seeded while River was in the table still carries the
    old binding, and blank-only repair would honor it forever. A binding
    that still equals byte for byte what the seed wrote is the seed's own
    work, and the seed may correct its own work."""
    client.post("/marketplace/seed", json={})
    conn = db.connect()
    pid = conn.execute(
        "SELECT profile_id FROM handles WHERE handle='pete_kowalski'"
    ).fetchone()["profile_id"]
    conn.execute(
        "UPDATE profile_voices SET voice_id=?, label=? WHERE profile_id=?",
        ("SAz9YHcvj6GT2YYXdXww", "River", pid))
    conn.commit()
    out = seed.repair()
    assert "pete_kowalski (voice)" in out["repaired_handles"]
    binding = spoken.bound(pid)
    assert binding["voice_id"] == seed.STARTER_VOICES["pete_kowalski"][0]
    assert binding["label"] == seed.STARTER_VOICES["pete_kowalski"][1]


def test_an_owners_own_binding_survives_the_recast(client):
    """The recast matches the seed's exact old work and nothing else — an
    owner who rebound the voice, whatever they chose, is never touched."""
    client.post("/marketplace/seed", json={})
    conn = db.connect()
    pid = conn.execute(
        "SELECT profile_id FROM handles WHERE handle='harold_jenkins'"
    ).fetchone()["profile_id"]
    conn.execute(
        "UPDATE profile_voices SET voice_id=?, label=? WHERE profile_id=?",
        ("v-harolds-own-pick", "My narrator", pid))
    conn.commit()
    seed.repair()
    assert spoken.bound(pid)["voice_id"] == "v-harolds-own-pick", (
        "the recast overwrote a binding an owner made")
