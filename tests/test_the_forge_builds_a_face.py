"""The forge: a photograph becomes a face, on this deployment's machine.

The round this file holds began as a purchase. The avatar shelf was an
import list and said so — *"nothing here calls a provider's API"* — and
the road chosen to fix that was Ready Player Me, which Netflix had
already bought and shut down, developer APIs and all, on 31 January
2026. The two production replacements price their API at eight hundred
dollars a month. The owner's call:

    "open source media pipe based pipelines generate GLB with ARKit
     blend shapes from a single photo, no vendor, no monthly bill"

So these are the guards on a road that runs at home. Three claims, and
the third is the one that keeps the second true next year:

1. The dead service is off the shelf, and nothing defaults to it.
2. A photograph becomes a head — and every way that can fail says so in
   words rather than handing somebody a placeholder face.
3. The provider is a **slot**. The blendshape names are ARKit's, so the
   renderer that draws one of our heads draws a bought one too, and a
   vendor's death costs a deployment an environment variable.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from qrme import avatarforge, avatars

REPO = Path(__file__).resolve().parents[1]
FORGE = (REPO / "qrme" / "avatarforge.py").read_text()
MAKER = (REPO / "docker" / "forge" / "facebuild.py").read_text()
RENDERER = (REPO / "app" / "src" / "Avatar3D.tsx").read_text()
IDENTITY = (REPO / "app" / "src" / "screens" / "Identity.tsx").read_text()


# -- the dead service is gone -------------------------------------------------

def test_the_shut_down_provider_is_off_the_shelf():
    keys = {row["key"] for row in avatars.MARKET}
    assert "ready_player_me" not in keys, (
        "the shelf offers a service that was shut down on 31 January "
        "2026 — a row that sends somebody to a dead door")
    # And the reason is written where the row used to be, so nobody
    # re-adds it in a year having forgotten why it went.
    source = (REPO / "qrme" / "avatars.py").read_text()
    assert "Netflix" in source and "31 January" in source


def test_no_client_opens_on_a_service_that_is_gone():
    """The defect this prevents is specific: three clients hard-coded
    the dead provider as their picker's opening value, so the dropdown
    would have opened on it even after the row was struck."""
    shells = [
        REPO / "native" / "ios" / "Sources" / "Views" / "FaceView.swift",
        (REPO / "native" / "android" / "app" / "src" / "main" / "java"
         / "app" / "qrme" / "studio" / "ui" / "Screens.kt"),
    ]
    for shell in shells:
        text = shell.read_text()
        assert 'chosenSource = "ready_player_me"' not in text
        assert 'mutableStateOf("ready_player_me")' not in text
    assert 'useState("ready_player_me")' not in IDENTITY


# -- the forge answers honestly -----------------------------------------------

def test_a_deployment_with_no_forge_says_so(monkeypatch):
    monkeypatch.delenv("QRME_FORGE_URL", raising=False)
    assert avatarforge.configured() is False
    assert avatarforge.doors()["configured"] is False
    with pytest.raises(avatarforge.ForgeError) as raised:
        avatarforge.from_photo(b"a picture")
    assert "no avatar forge configured" in str(raised.value)


def test_every_refusal_is_worded(monkeypatch):
    monkeypatch.setenv("QRME_FORGE_URL", "http://forge.test:8600")
    with pytest.raises(avatarforge.ForgeError) as empty:
        avatarforge.from_photo(b"")
    assert "empty" in str(empty.value)
    with pytest.raises(avatarforge.ForgeError) as big:
        avatarforge.from_photo(b"x" * (avatarforge.MAX_PHOTO_BYTES + 1))
    assert "larger than the forge takes" in str(big.value)
    with pytest.raises(avatarforge.ForgeError) as framing:
        avatarforge.from_photo(b"a picture", shot="sideways")
    assert "how the photo is framed" in str(framing.value)


def test_an_unreachable_forge_is_not_a_face(monkeypatch):
    """The failure this forbids: a forge that cannot be reached must not
    become a placeholder head somebody is told is theirs."""
    monkeypatch.setenv("QRME_FORGE_URL", "http://127.0.0.1:9")
    with pytest.raises(avatarforge.ForgeError) as raised:
        avatarforge.from_photo(b"a picture")
    assert "could not be reached" in str(raised.value)


def test_the_forge_passes_the_makers_own_refusal_through(monkeypatch):
    """A photograph with no face in it is the one failure a person can
    act on — send a clearer picture — so the sentence has to survive the
    trip rather than flattening into a status code."""
    import urllib.error
    import io

    monkeypatch.setenv("QRME_FORGE_URL", "http://forge.test:8600")

    def refuses(*a, **k):
        raise urllib.error.HTTPError(
            "http://forge.test/forge", 422, "Unprocessable", {},
            io.BytesIO(b'{"detail": "no face was found in that '
                       b'photograph"}'))

    monkeypatch.setattr("urllib.request.urlopen", refuses)
    with pytest.raises(avatarforge.ForgeError) as raised:
        avatarforge.from_photo(b"a picture")
    assert "no face was found" in str(raised.value)


# -- the provider is a slot ---------------------------------------------------

def test_the_blendshapes_are_arkits_names():
    """The interoperability claim, and the reason this round survives the
    next acquisition: a renderer driving `jawOpen` on one of our heads
    drives it on any vendor's model too."""
    named = avatarforge.doors()["blendshapes"]
    assert "jawOpen" in named
    assert set(named) == set(
        n for n in named if n[0].islower() and " " not in n)
    # The maker ships the same names, so the two ends cannot drift.
    for name in named:
        assert name in MAKER, f"the maker does not build {name}"
    # And the renderer looks them up BY NAME rather than by index, which
    # is what lets a bought model animate through the same code.
    assert 'set("jawOpen"' in RENDERER
    assert "morphTargetDictionary" in RENDERER


def test_an_unknown_provider_is_not_silently_a_working_one(monkeypatch):
    monkeypatch.setenv("QRME_AVATAR_PROVIDER", "some_vendor_we_invented")
    monkeypatch.setenv("QRME_FORGE_URL", "http://forge.test:8600")
    assert avatarforge.provider() == "none"
    assert avatarforge.configured() is False


# -- the door, and what it does with what comes back --------------------------

def test_the_forge_door_says_what_it_offers_before_anybody_uploads(client):
    r = client.get("/avatars/forge")
    assert r.status_code == 200
    out = r.json()
    assert set(out["shots"]) == {"face", "upper", "full"}
    assert "jawOpen" in out["blendshapes"]


def test_the_console_draws_the_road_only_where_there_is_one():
    """A button that fails is worse than an absence — and worst at the
    moment somebody has just chosen a photograph of themselves."""
    assert "forge?.configured &&" in IDENTITY
    for needle in ("idn.forge.face", "idn.forge.upper", "idn.forge.full",
                   "forgeFace", "forgeDoors"):
        assert needle in IDENTITY, f"the forge road lost {needle}"


def test_a_forged_face_is_not_stamped_as_synthetic():
    """The mark exists to stop a synthetic face passing as real. Burning
    it into somebody's own photographed face is that same failure run
    backwards, so the door mints the owner's own likeness."""
    router = (REPO / "qrme" / "routers" / "avatars.py").read_text()
    forged = router[router.index("def forge_face("):]
    forged = forged[:forged.index("@router.get(\"/avatars/market\")")]
    assert 'likeness="self"' in forged
    assert 'likeness="invented"' not in forged


def test_the_model_and_the_portrait_are_one_face(client, profile_id):
    """One registry row carries both forms, so a takedown done once is
    true for both. Split across two rows, every claim and every dispute
    would have to be done twice to be done at all."""
    from qrme import avatarreg
    row = avatarreg.mint(asset="https://example.test/face.png",
                         source="uploaded", provider="forge",
                         likeness="self")
    avatarreg.set_variant(row["id"], "model",
                          "https://example.test/head.glb")
    avatarreg.claim(row["id"], profile_id)
    shown = client.get(f"/profiles/{profile_id}/avatar").json()
    assert shown["model"] == "https://example.test/head.glb"
    # Retired: the model leaves with the portrait rather than outliving
    # the takedown.
    avatarreg.retire(row["id"], because="a test of the takedown")
    assert avatars.model_of(profile_id) is None


def test_a_glb_is_stored_under_its_own_name():
    """The console's renderer is handed a `.glb` and not a `.txt`: the
    format's own magic proves the label, the way every other kind in the
    media layer is proved."""
    from qrme import media
    assert media._sniff(b"glTF" + b"\x02\x00\x00\x00" + b"\x00" * 32) \
        == ("file", ".glb")
