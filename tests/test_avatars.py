"""Profile portraits: the badge, the rights record, and the art direction.

The interesting failures here are not crashes. They are a synthetic face
reaching a viewer without its AI disclosure, a real person's likeness on a
profile with no record of the grant, and a joke portrait on the profile
somebody opens during a crisis. Each has a test.
"""

from qrme import avatars, db, seed


def _profile_body(**over):
    body = {"owner_id": "owner-1", "kind": "fictional",
            "display_name": "Ada", "persona": "A careful engineer.",
            "verification": {"birthdate": "1990-01-01",
                             "id_document": "passport",
                             "liveness_check": True}}
    body.update(over)
    return body


def test_avatar_always_carries_the_ai_badge(client):
    """The portrait is the most-looked-at render QRME produces. It cannot be
    fetched without the disclosure attached — surfaces composite the badge,
    they do not decide whether to."""
    created = client.post("/profiles", json=_profile_body()).json()
    pid, token = created["id"], created["owner_token"]
    client.put(f"/profiles/{pid}/avatar", json={"asset": "avatars/ada.png"},
               headers={"authorization": f"Bearer {token}"})

    body = client.get(f"/profiles/{pid}/avatar").json()
    assert body["asset"] == "avatars/ada.png"
    assert body["watermark"]["always_displayed"] is True
    assert "AI" in body["watermark"]["line"]
    assert body["placeholder"] is False


def test_a_custom_watermark_still_declares_ai_on_the_portrait(client):
    """Owners design their own mark; the AI designation is not designable
    away, and that has to hold on the avatar surface too."""
    created = client.post("/profiles", json=_profile_body()).json()
    pid, token = created["id"], created["owner_token"]
    auth = {"authorization": f"Bearer {token}"}
    client.put(f"/profiles/{pid}/watermark",
               json={"mark": "☾", "label": "Ada of the Loom"}, headers=auth)
    client.put(f"/profiles/{pid}/avatar", json={"asset": "a.png"}, headers=auth)

    line = client.get(f"/profiles/{pid}/avatar").json()["watermark"]["line"]
    assert line.startswith("☾")
    assert "AI" in line


def test_a_profile_with_no_portrait_says_so_rather_than_faking_one(client):
    """No asset is an answer: fall back to initials, never an unbadged
    placeholder image."""
    pid = client.post("/profiles", json=_profile_body()).json()["id"]
    body = client.get(f"/profiles/{pid}/avatar").json()
    assert body["asset"] is None
    assert body["placeholder"] is True
    assert body["watermark"]["always_displayed"] is True


def test_only_the_owner_can_attach_a_portrait(client):
    created = client.post("/profiles", json=_profile_body()).json()
    pid = created["id"]
    assert client.put(f"/profiles/{pid}/avatar",
                      json={"asset": "x.png"}).status_code in (401, 403)


def test_an_invented_face_reports_no_rights_holder(client):
    pid = client.post("/profiles", json=_profile_body()).json()["id"]
    likeness = client.get(f"/profiles/{pid}/avatar").json()["likeness"]
    assert likeness["real_person"] is False


def test_a_real_likeness_carries_its_grant_on_the_portrait(client):
    """Permission given in conversation is not a record. A profile wearing a
    real person's face reports who granted it and that it can be withdrawn."""
    created = client.post("/profiles", json=_profile_body(
        kind="other_person", display_name="Dave",
        consent={"basis": "subject_consent", "attestor": "dave"})).json()
    pid, token = created["id"], created["owner_token"]
    client.put(f"/profiles/{pid}/avatar", json={"asset": "dave.png"},
               headers={"authorization": f"Bearer {token}"})

    likeness = client.get(f"/profiles/{pid}/avatar").json()["likeness"]
    assert likeness["real_person"] is True
    assert likeness["basis"] == "subject_consent"
    assert likeness["attestor"] == "dave"
    assert likeness["revocable"] is True


def test_a_real_likeness_cannot_be_created_without_a_grant(client):
    """The rule that makes the record above meaningful — already enforced at
    creation, asserted here because the avatar work depends on it."""
    r = client.post("/profiles", json=_profile_body(kind="other_person"))
    assert r.status_code == 422


def test_a_real_likeness_can_never_be_rated(client):
    """rated.py's hard line: adult mode is never available for a profile of
    another real person. A funny costume idea does not get to reopen this."""
    r = client.post("/profiles", json=_profile_body(
        kind="other_person", adult_mode=True,
        consent={"basis": "subject_consent", "attestor": "dave"}))
    assert r.status_code == 403


def test_every_starter_has_a_portrait_brief():
    """A starter without art direction ships facelessly, which is how the
    collection ends up half stock photos."""
    handles = {handle for handle, *_ in seed.STARTERS + seed.RATED}
    assert handles <= set(avatars.BRIEFS), handles - set(avatars.BRIEFS)


def test_briefs_state_their_own_constraints():
    """The constraints have to survive being pasted into a tool somewhere
    else, so they ride inside the brief rather than living only in docs."""
    for brief in avatars.catalog():
        joined = " ".join(brief["constraints"]).lower()
        assert "not a likeness of anyone real" in joined
        assert "trademarked" in joined
        # The rated portrait carries its own treatment (RATED_STYLE): it is
        # age-walled off every surface the others appear on, so matching the
        # collection's look would buy nothing.
        assert brief["prompt"].endswith(brief["style"])
        assert brief["style"] in (avatars.STYLE, avatars.RATED_STYLE)


def test_the_mental_health_trio_are_not_played_for_laughs():
    """A joke portrait on the profile someone reaches in a bad hour is a joke
    at their expense. JIM-mini's Guardian escalates to these three."""
    for handle in ("dr_lena_whitcomb", "dr_marcus_adeyemi", "dr_priya_nair"):
        assert avatars.brief(handle)["tone"] == "sombre"
    assert avatars.brief("marcus_bell")["tone"] == "humorous"


def test_unknown_handle_has_no_brief(client):
    assert avatars.brief("nobody_here") is None
    assert client.get("/avatars/briefs/nobody_here").status_code == 404


def test_the_brief_sheet_is_public(client):
    """It is the honest answer to 'where did these faces come from' — every
    one is an invented person, and the briefs say so."""
    body = client.get("/avatars/briefs").json()
    assert body["style"] == avatars.STYLE
    assert len(body["briefs"]) == len(avatars.BRIEFS)


def test_seeded_starters_look_like_their_portraits(client):
    """The brief doubles as the profile's `appearance`, which rides on the
    prompt — so the face and the voice describe the same character."""
    client.post("/marketplace/seed")
    card = client.get("/summon", params={"ref": "@marcus_bell"}).json()
    pid = card["profile"]["profile_id"]
    # `appearance` is steering state, not a public field, so read it where it
    # is stored rather than through an owner-gated endpoint.
    row = db.connect().execute(
        "SELECT appearance FROM profiles WHERE id=?", (pid,)).fetchone()
    assert row["appearance"] == avatars.BRIEFS["marcus_bell"]
    assert "gold" in row["appearance"].lower()


def test_the_rated_starter_is_age_walled_like_any_other(client):
    """Seeding a rated profile only ships an empty shelf's worth of content —
    it does not put it in front of anyone the existing gate wouldn't stop."""
    client.post("/marketplace/seed")
    card = client.get("/summon", params={"ref": "@vivienne_sable"}).json()
    assert card["profile"].get("rated") is True
    assert card["profile"].get("age_wall") or "18" in str(card["profile"])


# --- the shipped collection ----------------------------------------------

def test_every_starter_ships_with_a_portrait():
    """A starter with no face falls back to initials on the beacon page and
    in the camera overlay — which is the first thing a stranger ever sees of
    this product."""
    missing = [handle for handle in avatars.BRIEFS
               if avatars.asset_path(handle) is None]
    assert not missing, f"no portrait file for: {missing}"


def _webp_size(raw: bytes) -> tuple[int, int]:
    """Dimensions straight out of the simple-lossy WebP header.

    Read here rather than through an imaging library so the test suite does
    not gain a dependency it needs for one assertion — and so what is checked
    is the shipped container itself, not a library's reading of it.
    """
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", "not a WebP file"
    assert raw[12:16] == b"VP8 ", f"unexpected WebP chunk {raw[12:16]!r}"
    assert raw[23:26] == b"\x9d\x01\x2a", "bad VP8 start code"
    return (int.from_bytes(raw[26:28], "little") & 0x3FFF,
            int.from_bytes(raw[28:30], "little") & 0x3FFF)


def test_the_portraits_are_square_and_small_enough_to_load_on_cellular():
    """The beacon page renders them in a 1:1 frame, and it opens in a camera
    app's in-app browser on a cold start."""
    for path in sorted(avatars.portraits_dir().glob("*.webp")):
        size = _webp_size(path.read_bytes())
        assert size == (512, 512), f"{path.name} is {size}"
        assert path.stat().st_size < 120_000, f"{path.name} is heavy"


def test_the_portrait_directory_is_declared_as_package_data():
    """These files live inside the package, so they vanish on `pip install`
    unless setuptools is told to carry them. That failure is invisible in the
    repo and total in the container — the same shape as the /app 404."""
    import pathlib
    toml = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = toml.read_text()
    assert "[tool.setuptools.package-data]" in text
    assert "assets/portraits/*.webp" in text


def test_seeded_starters_carry_their_portrait(client):
    from qrme import seed
    seed.seed()
    pid = client.get("/summon?ref=@dr_amara_osei").json()["profile"]["profile_id"]
    art = client.get(f"/profiles/{pid}/avatar").json()
    assert art["asset"] == "/portraits/dr_amara_osei.webp"
    assert art["placeholder"] is False
    # The badge is attached at the source, never left to the surface.
    assert art["watermark"]["always_displayed"] is True


def test_a_portrait_is_actually_served(client):
    res = client.get("/portraits/coach_dana_reyes.webp")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/webp"


def test_a_starters_face_belongs_to_nobody(client):
    """The whole collection is invented people, so no starter reports a
    rights holder — that is what makes shipping them everywhere safe."""
    from qrme import seed
    seed.seed()
    pid = client.get("/summon?ref=@otis_marsh").json()["profile"]["profile_id"]
    art = client.get(f"/profiles/{pid}/avatar").json()
    assert art["likeness"]["real_person"] is False
    assert "no rights holder" in art["likeness"]["note"]
