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
    """No portrait is an answer, and now it is *one* answer.

    This used to assert `asset is None`, on the reasoning that surfaces
    should "fall back to initials, never an unbadged placeholder image". The
    first half was the defect: three surfaces fell back three different ways
    — initials on Home and the Top 8, an abstract orb on the talk surface,
    the empty frame for an anonymous profile — so the same profile had three
    faces and the one on the conversation screen made every portrait-less
    person look identical.

    The property the test was really protecting is the second half, and it
    still holds exactly: `placeholder` stays true, so nothing captions the
    frame as somebody's face, and the badge is still always displayed.
    """
    pid = client.post("/profiles", json=_profile_body()).json()["id"]
    body = client.get(f"/profiles/{pid}/avatar").json()
    assert body["asset"] == avatars.ADD_PHOTO
    assert body["placeholder"] is True
    # Not their own face, so nothing may claim the mark is in these pixels.
    assert body["asset_marked"] is False
    assert body["watermark"]["always_displayed"] is True


def test_the_frame_is_the_only_answer_to_a_missing_face(client):
    """One picture, whichever way the profile got here.

    A profile with no portrait and an anonymous profile that has chosen
    nothing arrive at the same frame — which is the point: *two defaults
    meant two things that could disagree about the same profile*, and there
    were three.
    """
    created = client.post("/profiles", json=_profile_body()).json()
    pid = created["id"]
    auth = {"authorization": f"Bearer {created['owner_token']}"}
    plain = client.get(f"/profiles/{pid}/avatar").json()

    veiled = client.put(f"/profiles/{pid}/anonymity",
                        json={"anonymous": True}, headers=auth)
    assert veiled.status_code == 200, veiled.text
    hidden = client.get(f"/profiles/{pid}/avatar").json()

    assert plain["asset"] == hidden["asset"] == avatars.ADD_PHOTO
    # The flags still tell the two apart — one is veiled, one is merely bare.
    assert plain["silhouette"] is False and hidden["silhouette"] is True


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


def test_every_portrait_has_a_bubble_for_the_readme():
    """The README embeds these directly, and GitHub strips the `style`
    attribute that would round them — so a portrait without a baked bubble
    renders as the hard-edged black box the shipped file actually is.

    That is invisible in the repo and obvious on the project's front page, so
    a newly added portrait must not be able to reintroduce it quietly.
    """
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    bubbles = root / "docs" / "portraits" / "bubbles"
    shipped = {p.name for p in avatars.portraits_dir().glob("*.webp")}
    baked = {p.name for p in bubbles.glob("*.webp")}
    missing = sorted(shipped - baked)
    assert not missing, (
        f"no README bubble for {', '.join(missing)} — "
        "run `python3 tools/bubble_portraits.py`")


def test_the_bubbles_keep_their_transparency():
    """The bubble's corners and glow margin must be alpha, not a dark fill.
    Baking a background in would be the black box again by another route, and
    would read as a grey slab in GitHub's light theme."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    sample = root / "docs" / "portraits" / "bubbles" / "marcus_bell.webp"
    raw = sample.read_bytes()
    # VP8L / VP8X with the alpha bit is how a WebP carries transparency.
    assert b"ALPH" in raw[:64] or b"VP8L" in raw[:64], \
        "bubble has no alpha channel; the corners would render filled"


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


# --- the mark is in the pixels, not only in the chrome --------------------

def test_every_shipped_portrait_matches_the_checksum_manifest():
    """The bytes stay pinned even though the mark no longer lives in them.

    The manifest was written to catch a marked portrait being swapped for
    an unmarked one. The mark is drawn by the surface now, so that is no
    longer what it guards — what it still guards is a shipped face being
    replaced by a different image without the suite noticing, which is
    the part that was always doing the work."""
    import hashlib
    import json
    directory = avatars.portraits_dir()
    manifest = json.loads((directory / "MANIFEST.json").read_text())
    shipped = sorted(p.name for p in directory.glob("*.webp"))
    assert sorted(manifest) == shipped, "manifest and directory disagree"
    for name in shipped:
        digest = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        assert manifest[name] == digest, f"{name} is not the marked file"


def test_no_shipped_portrait_claims_to_carry_its_own_mark(client):
    """Because none of them do any more, and the surfaces read this flag.

    The AI label is drawn on top of the profile photo sphere rather than
    burned into the photograph — a circle crops the corner of a square,
    so a burned mark shipped sliced in half. `asset_marked: False` is
    what tells every surface to draw its own. A stale True here would
    mean each one politely skipping the badge that is no longer there."""
    from qrme import seed
    seed.seed()
    pid = client.get("/summon?ref=@dr_amara_osei").json()["profile"]["profile_id"]
    art = client.get(f"/profiles/{pid}/avatar").json()
    assert art["asset_marked"] is False


def test_an_owner_attached_asset_is_never_assumed_to_be_marked(client):
    """Nothing here can vouch for somebody else's file, so the surfaces keep
    drawing their own badge over it — the safe direction to be wrong in."""
    created = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "display_name": "Marcus Bell",
        "persona": "A planner.",
        "verification": {"birthdate": "1980-01-01", "id_document": "passport",
                         "liveness_check": True}}).json()
    client.put(f"/profiles/{created['id']}/avatar",
               json={"asset": "https://example.test/face.png"},
               headers={"authorization": f"Bearer {created['owner_token']}"})
    art = client.get(f"/profiles/{created['id']}/avatar").json()
    assert art["asset"] == "https://example.test/face.png"
    assert art["asset_marked"] is False


def test_a_portrait_is_served_as_the_exact_file_that_was_shipped(client):
    """The route hands back the shipped bytes, unchanged and unsubstituted.

    This test used to assert the opposite thing about the same bytes:
    that they carried the AI mark, because /portraits/{handle}.webp is an
    ordinary file URL that can be hotlinked, embedded, scraped or saved,
    and a composited badge survives none of that. The mark moved onto the
    sphere by decision, and that gap is open again — written down in
    docs/media-provenance.md rather than left for somebody to discover.

    What is still worth pinning: the route serves the file the manifest
    describes, so a swapped or re-encoded portrait fails here."""
    import hashlib
    import json
    res = client.get("/portraits/otis_marsh.webp")
    assert res.status_code == 200
    manifest = json.loads(
        (avatars.portraits_dir() / "MANIFEST.json").read_text())
    assert hashlib.sha256(res.content).hexdigest() == manifest["otis_marsh.webp"]
