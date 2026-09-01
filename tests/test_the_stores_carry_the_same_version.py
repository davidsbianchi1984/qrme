"""The stores room rides the release train.

    asked     put the product on the shelves — Meta Horizon as a
              packaged PWA, Steam and Viveport as thin launchers
    mattered  a shelf showing last month's number is a stale claim
              about the product; the release train must not be able to
              leave the stores room behind

The developer-account credentials and app IDs are deliberately absent
from the repo — each counter's README names where they are entered.
What CAN be held here is agreement: every manifest in `stores/` carries
the version `app/package.json` carries, and every screenshot the shared
listing names is a file that exists.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _app_version() -> str:
    return json.loads((ROOT / "app/package.json").read_text())["version"]


def test_the_quest_manifest_carries_the_version():
    m = json.loads((ROOT / "stores/meta-horizon/manifest.json").read_text())
    assert m["versionName"] == _app_version()
    # The versionCode follows the Android shell's 2009XXX scheme, so the
    # four package roads agree on what number a release is.
    gradle = (ROOT / "native/android/app/build.gradle.kts").read_text()
    code = int(re.search(r"versionCode = (\d+)", gradle).group(1))
    assert m["versionCode"] == code, (
        "the Quest package and the Android shell disagree on versionCode")


def test_the_steam_desc_carries_the_version():
    vdf = (ROOT / "stores/steam/app_build.vdf").read_text()
    assert f'"Desc" "QRME Studio {_app_version()}"' in vdf


def test_the_viveport_manifest_carries_the_version():
    m = json.loads((ROOT / "stores/viveport/app.json").read_text())
    assert m["app_version"] == _app_version()


def test_every_screenshot_the_listing_names_exists():
    """The listing is the one description all three counters share; a
    named screenshot that is not in the repo would make the shared copy
    a promise the upload step cannot keep."""
    listing = (ROOT / "stores/listing.md").read_text()
    named = re.findall(r"`(docs/screens/[^`]+\.png)`", listing)
    assert named, "the listing names no screenshots at all"
    missing = [p for p in named if not (ROOT / p).is_file()]
    assert not missing, f"listing names screenshots that do not exist: {missing}"


def test_no_credential_shaped_string_lives_in_the_stores_room():
    """The counters hold placeholders, never the things themselves."""
    for path in (ROOT / "stores").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".vdf", ""}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for word in ("api_key", "apikey", "secret=", "token=",
                         "password", "Bearer "):
                assert word not in text, (path, word)
    vdf = (ROOT / "stores/steam/app_build.vdf").read_text()
    assert "<STEAM_APP_ID>" in vdf, (
        "a real Steam App ID must be filled on the owner's machine, "
        "never committed")
