"""What kind of thing the face is, and what the conversation is doing.

``avatars.render`` has said since it was written that "2-D, 3-D, VR and AR
surfaces all read this one shape", and the shape was a URL. The import shelf
has offered Ready Player Me's ``.glb`` link the whole time, so an owner could
already hand this platform a 3-D model, and every surface downstream would
put it in an ``<img>``.

    asked     can a profile carry more than a still picture
    mattered  can a surface tell what it was handed
"""

from __future__ import annotations

import pytest

from qrme import presentation


# --------------------------------------------------------------------------- #
# The kind is read from the asset, not from what anybody claimed
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("asset,kind", [
    ("/portraits/osei.webp", "image"),
    ("https://cdn.test/figure.glb", "model"),
    ("https://cdn.test/figure.gltf", "model"),
    ("https://cdn.test/avatar.vrm", "model"),
    ("https://cdn.test/loop.mp4", "video"),
    ("https://cdn.test/loop.webm", "video"),
    ("https://cdn.test/scene/room.html", "scene"),
    (None, "image"),
    ("", "image"),
])
def test_the_address_says_what_it_is(asset, kind):
    assert presentation.kind_of(asset) == kind


def test_a_signed_url_is_still_what_it_is():
    """`…/figure.glb?sig=…&exp=…` is a model. Reading the tail literally
    called it an image, which is the exact failure this module exists for."""
    assert presentation.kind_of(
        "https://cdn.test/figure.glb?sig=abc&exp=99") == "model"
    assert presentation.kind_of("https://cdn.test/loop.mp4#t=2") == "video"


def test_an_address_that_says_nothing_is_an_image():
    """The safe guess: it is what every surface already did with an unknown
    URL, so being wrong here changes nothing that was not already so."""
    assert presentation.kind_of("https://cdn.test/v1/avatar/8831") == "image"


# --------------------------------------------------------------------------- #
# The owner's own answer, for an address that cannot say
# --------------------------------------------------------------------------- #

def test_the_owner_can_say_what_an_opaque_address_holds(
        client, profile_id):
    opaque = "https://cdn.test/v1/avatar/8831"
    put = client.put(f"/profiles/{profile_id}/avatar",
                     json={"asset": opaque, "presentation_kind": "model"})
    assert put.status_code == 200, put.text
    shown = client.get(f"/profiles/{profile_id}/avatar").json()["presentation"]
    assert shown["kind"] == "model"
    # Flagged as a claim rather than a reading, so a surface may weigh it.
    assert shown["declared"] is True


def test_clearing_the_override_hands_the_question_back_to_the_address(
        client, profile_id):
    client.put(f"/profiles/{profile_id}/avatar",
               json={"asset": "https://cdn.test/x.png",
                     "presentation_kind": "model"})
    client.put(f"/profiles/{profile_id}/avatar",
               json={"asset": "https://cdn.test/x.png",
                     "presentation_kind": ""})
    shown = client.get(f"/profiles/{profile_id}/avatar").json()["presentation"]
    assert shown["kind"] == "image" and shown["declared"] is False


def test_a_kind_nobody_renders_is_refused(client, profile_id):
    bad = client.put(f"/profiles/{profile_id}/avatar",
                     json={"asset": "https://cdn.test/x",
                           "presentation_kind": "hologram"})
    assert bad.status_code == 422
    assert "image" in bad.json()["detail"]


# --------------------------------------------------------------------------- #
# It rides the shape every surface already reads
# --------------------------------------------------------------------------- #

def test_the_presentation_arrives_with_the_badge_and_not_apart_from_it(
        client, profile_id):
    """No second door. A client that can reach the picture can reach the fact
    of what the picture is, because they are the same response — the reason
    the AI badge is attached here too."""
    client.put(f"/profiles/{profile_id}/avatar",
               json={"asset": "https://cdn.test/figure.glb"})
    shown = client.get(f"/profiles/{profile_id}/avatar").json()
    assert shown["presentation"]["kind"] == "model"
    assert shown["watermark"] is not None


def test_every_client_is_told_the_states_rather_than_compiled_with_them(
        client, profile_id):
    """A shell that renders the set it was built with is a shell that becomes
    the odd one out the first time the set changes."""
    shown = client.get(f"/profiles/{profile_id}/avatar").json()["presentation"]
    assert shown["presence_states"] == list(presentation.PRESENCE)
    assert shown["presence_default"] == "idle"
    # Calm, not broken: a client that has not been taught the states yet must
    # not sit in `error`.
    assert shown["presence_default"] != "error"


def test_the_still_is_what_a_surface_falls_back_to(client, profile_id):
    """A console that cannot run a model still has something to draw, and the
    field says which thing rather than leaving each surface to guess."""
    client.put(f"/profiles/{profile_id}/avatar",
               json={"asset": "https://cdn.test/figure.glb"})
    shown = client.get(f"/profiles/{profile_id}/avatar").json()["presentation"]
    # No torso attached, and the asset is not itself an image, so there is
    # honestly nothing to fall back to — reported as None rather than as the
    # model URL, which an `<img>` would render as a broken picture.
    assert shown["still"] is None

    client.put(f"/profiles/{profile_id}/avatar",
               json={"asset": "/portraits/osei.webp"})
    shown = client.get(f"/profiles/{profile_id}/avatar").json()["presentation"]
    assert shown["still"] == "/portraits/osei.webp"


def test_an_anonymous_profile_falls_back_to_no_face_of_its_own(
        client, profile_id):
    """The silhouette substitution happens in `render`, and the presentation
    block must not route around it — a torso is a picture of somebody too."""
    client.put(f"/profiles/{profile_id}/avatar",
               json={"asset": "https://cdn.test/figure.glb"})
    veiled = client.put(f"/profiles/{profile_id}/anonymity",
                        json={"anonymous": True})
    assert veiled.status_code == 200, veiled.text
    shown = client.get(f"/profiles/{profile_id}/avatar").json()
    assert shown["silhouette"] is True
    assert shown["presentation"]["still"] != "https://cdn.test/figure.glb"
