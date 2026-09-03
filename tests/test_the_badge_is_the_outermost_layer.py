"""The AI badge on rendered footage: outermost on screen, burned on download.

    asked     the AI badge is the outermost overlay of any video rendered,
              not in the image; expanding to full screen does not hide
              it; a download carries it burned in
    mattered  a badge the page draws is not in the file, and a badge in
              the file cannot be the page's outermost layer — so there
              are two, and each has to be checked where it lives
"""
from __future__ import annotations

import io
import re
import shutil
from pathlib import Path

import pytest

from qrme import badge, media

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "app" / "src"


def _players() -> list[str]:
    return [(SRC / n).read_text(encoding="utf-8")
            for n in ("SceneFilm.tsx", "SeatFilm.tsx")]


def test_the_players_own_fullscreen_and_download_are_switched_off():
    """The browser's own full-screen shows the bare video element with no
    badge on it, and its own download hands out the unburned file. Every
    rendered-footage player turns both off, so the only way to fill the
    screen is the takeover that carries the badge, and the only download
    is the burned copy."""
    for src in _players():
        videos = re.findall(r"<video\b[^>]*>", src, re.S)
        assert videos, "no <video> in a film player"
        for v in videos:
            assert "nofullscreen" in v and "nodownload" in v, v


def test_the_takeover_carries_the_badge_above_the_player():
    for src in _players():
        over = src[src.index('className="rs-film-over"'):]
        over = over[:over.index("</div>")]
        assert "rs-film-ai" in over, (
            "the full-screen takeover draws the video without the badge — "
            "expanding hides it")
    css = (REPO / "app" / "src" / "styles.css").read_text(encoding="utf-8")
    m = re.search(r"\.rs-film-over \.rs-film-ai \{([^}]*)\}", css)
    assert m and "z-index" in m.group(1), (
        "the badge on the takeover has no layer of its own above the player")


def test_every_player_offers_the_burned_download():
    for src in _players():
        assert '/download"' in src and "rs-film-down" in src, (
            "a film player offers no download — or offers the unburned file")


def test_an_authentic_upload_is_never_burned(client):
    """The mark exists to say what is synthetic. Stamping a photograph
    somebody uploaded is a false statement in the other direction."""
    from PIL import Image
    buf = io.BytesIO(); Image.new("RGB", (64, 64), "white").save(buf, "PNG")
    row = media.save("prf_test", buf.getvalue(), name="real.png")
    with pytest.raises(badge.NoBadge):
        badge.burned(row["id"])
    assert client.get(f"/media/{row['id']}/download").status_code == 404


def test_a_rendered_picture_downloads_with_the_badge_in_its_pixels(client):
    from PIL import Image
    buf = io.BytesIO(); Image.new("RGB", (320, 180), "white").save(buf, "PNG")
    row = media.save("prf_test", buf.getvalue(), name="scene.png",
                     ai_marked=True)
    r = client.get(f"/media/{row['id']}/download")
    assert r.status_code == 200, r.text
    assert "attachment" in r.headers["content-disposition"]
    burned = Image.open(io.BytesIO(r.content)).convert("RGB")
    assert burned.getpixel((badge.MARGIN + 4, badge.MARGIN + 4)) != (255, 255, 255), (
        "the corner is still white — nothing burned")
    assert burned.getpixel((300, 170)) == (255, 255, 255), (
        "the badge spread past its corner")


def test_footage_without_a_burner_is_refused_not_served_unmarked(client, monkeypatch):
    row = media.save("prf_test", b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64,
                     name="scene.mp4", ai_marked=True)
    monkeypatch.setattr(shutil, "which", lambda name: None)
    r = client.get(f"/media/{row['id']}/download")
    assert r.status_code == 503 and "ffmpeg" in r.json()["detail"]
