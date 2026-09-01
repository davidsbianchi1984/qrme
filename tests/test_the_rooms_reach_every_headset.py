"""The XR shelf: every headset on the market, and its honest road in.

The owner's brief, three messages wide: Steam outputs for the VR rooms,
Meta and Apple for the glasses, "and any others that are available in the
market — let's go ahead and cover all the competitors and offer their
tools." The architecture that makes the brief true today is that the
rooms are web pages: the AR and VR stages run on WebXR, so every vendor's
road in is its own browser, named per row. What is NOT built — native
apps, platform sign-ins — is marked planned, in the grey-button doctrine
qrme/oauth.py wrote down.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_the_shelf_covers_the_market(client):
    got = client.get("/rooms/xr-platforms")
    assert got.status_code == 200, got.text
    rows = {r["platform"]: r for r in got.json()["xr_platforms"]}
    for vendor in ("phone", "meta", "apple", "steam", "pico", "htc",
                   "android_xr"):
        assert vendor in rows, f"the shelf lost {vendor}"
    assert rows["steam"]["wears"] == ["vr"]
    assert "ar" in rows["apple"]["wears"], (
        "the glasses vendor lost its AR badge")


def test_every_open_row_names_its_road_and_no_app_is_invented(client):
    rows = client.get("/rooms/xr-platforms").json()["xr_platforms"]
    for r in rows:
        if r["open_now"]:
            assert r["browser"], f"{r['platform']} claims open with no road"
        assert r["native_app"] == "planned", (
            f"{r['platform']} claims a native app nobody has shipped")


def test_signin_states_mirror_the_real_doors(client):
    """`live`/`unconfigured` read from oauth.py's registry, never asserted
    by hand; the doors that do not exist say planned; a vendor with no
    account of its own here says none."""
    from qrme import oauth
    doors = {p["provider"]: p["configured"]
             for p in oauth.providers()["signin_providers"]}
    rows = {r["platform"]: r for r in
            client.get("/rooms/xr-platforms").json()["xr_platforms"]}
    assert rows["apple"]["signin"] == (
        "live" if doors.get("apple") else "unconfigured")
    assert rows["android_xr"]["signin"] == (
        "live" if doors.get("google") else "unconfigured")
    assert rows["steam"]["signin"] == "planned"
    assert rows["meta"]["signin"] == "planned"
    assert rows["phone"]["signin"] == "none"


def test_the_console_offers_the_shelf():
    api_src = (REPO / "app/src/api.ts").read_text(encoding="utf-8")
    rooms = (REPO / "app/src/screens/Rooms.tsx").read_text(encoding="utf-8")
    assert "xrPlatforms" in api_src
    assert "xrPlatforms" in rooms and "rms.xr.title" in rooms


def test_the_pull_door_answers_honestly(client, monkeypatch):
    """The one-button fill for the deployment shelf, in its three states:
    no key is a refusal in a sentence; a key against the door the provider
    has not opened is a zero with a machine word; a provider that answers
    stocks the shelf, provider_asset_id and all."""
    monkeypatch.setenv("QRME_SIGNUP_KEY", "op-secret")
    op = {"x-signup-key": "op-secret"}

    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    r = client.post("/avatars/library/pull", headers=op)
    assert r.status_code == 503
    assert "ELEVENLABS_API_KEY" in r.json()["detail"]

    monkeypatch.setenv("ELEVENLABS_API_KEY", "xi-test")
    import urllib.request as rq

    def closed(*a, **k):
        raise OSError("no such door")
    monkeypatch.setattr(rq, "urlopen", closed)
    r = client.post("/avatars/library/pull", headers=op)
    assert r.status_code == 200
    assert r.json() == {"pulled": 0, "note": "provider_door_closed"}

    import io
    import json as js

    class FakeAnswer(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def open_door(*a, **k):
        return FakeAnswer(js.dumps({"avatars": [
            {"avatar_id": "Pa8eJnd8sLPAX5u88jZH", "name": "David Bianchi",
             "image_url": "https://cdn.example/avatar.png"},
            {"avatar_id": "av_2", "name": "No picture"},
        ]}).encode("utf-8"))
    monkeypatch.setattr(rq, "urlopen", open_door)
    r = client.post("/avatars/library/pull", headers=op)
    assert r.status_code == 200
    assert r.json() == {"pulled": 1, "note": "stocked"}
    shelf = client.get("/avatars/library").json()["shelf"]
    row = next(x for x in shelf
               if x["provider_asset_id"] == "Pa8eJnd8sLPAX5u88jZH")
    assert row["provider"] == "elevenlabs" and row["label"] == "David Bianchi"

    nobody = client.post("/avatars/library/pull")
    assert nobody.status_code == 403, "anybody could stock the shelf"
