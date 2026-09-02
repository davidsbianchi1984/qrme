"""The model menu is a loadout per region, and a lever tapers it.

    asked     which providers does this platform know
    mattered  which providers is THIS account offered

The registry knows every provider and where it is from. What an account
sees depends on where it signed up: home providers first, then a curated
few popular foreign ones for that market. A US account is American-led with
a handful of the foreign models people actually ask for; a Chinese account
leads with Qwen, DeepSeek, Kimi and GLM; Europe leads with Mistral. And the
one-line lever — ``QRME_MODEL_POLICY=american`` — tapers the *American-
region* menu to American, local and self-supplied providers, binding no
other region. The video shelf is the same shape.

The region is a fact on the account, chosen at sign-up and editable on
Settings. A profile inherits its owner's; a profile whose owner is not an
account here stands on the default rather than being refused a menu.
"""

from __future__ import annotations

import pytest

from qrme import filming, llm, loadouts

from . import ratchets


def _account(client, region=None):
    body = {"email": f"{region or 'x'}@example.com", "password": "longenough1"}
    if region:
        body["region"] = region
    r = client.post("/signup", json=body)
    assert r.status_code == 201, r.text
    got = r.json()
    assert got["verification"] == "local"     # no SMTP in the suite
    return got["account_id"], got["account_token"]


def _profile_of(client, account_id):
    r = client.post("/profiles", json={
        "owner_id": account_id, "kind": "self", "display_name": "Dana",
        "persona": "A retired teacher.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert r.status_code == 201, r.text
    client.headers["authorization"] = f"Bearer {r.json()['owner_token']}"
    return r.json()["id"]


# --- the registry ------------------------------------------------------------

def test_the_registry_is_wide_and_every_provider_names_its_home():
    real = [n for n, s in llm._REGISTRY.items()
            if s.get("origin") not in ("local", "any")]
    assert len(real) >= ratchets.floor("llm.real_providers"), (
        f"only {len(real)} real providers on the menu")
    for name, spec in llm._REGISTRY.items():
        assert spec.get("origin"), f"{name} has no origin"
    assert all("origin" in row for row in llm.available())


def test_every_loadout_names_only_providers_the_registry_has():
    for region, names in loadouts.LOADOUTS.items():
        missing = [n for n in names if n not in llm._REGISTRY]
        assert not missing, f"{region} offers {missing}, which do not exist"
    assert set(loadouts.LOADOUTS) == set(loadouts.REGIONS)


# --- the loadouts ------------------------------------------------------------

def test_a_profile_with_no_account_stands_on_the_default(client, profile_id):
    """`owner-1` is not an account; the suite's own profile is the case."""
    assert loadouts.region_of(profile_id) == loadouts.DEFAULT_REGION
    assert loadouts.providers_for(profile_id)[0] == "anthropic"


def test_a_us_account_is_american_led_with_a_curated_few_foreign(client):
    acc, _ = _account(client, "us")
    pid = _profile_of(client, acc)
    names = loadouts.providers_for(pid)
    assert names[0] == "anthropic"                    # the beta default leads
    assert "deepseek" in names and "mistral" in names  # a curated few foreign
    assert "zhipu" not in names                       # not every foreign one
    assert set(loadouts._LOCAL) <= set(names)         # local always offered


def test_a_chinese_account_leads_with_its_home_providers(client):
    acc, _ = _account(client, "cn")
    pid = _profile_of(client, acc)
    names = loadouts.providers_for(pid)
    assert names[0] == "qwen" and "zhipu" in names
    assert "anthropic" in names                        # and still offers American


def test_the_region_is_chosen_at_sign_up_and_editable_after(client):
    acc, tok = _account(client, "jp")
    pid = _profile_of(client, acc)
    assert loadouts.region_of(pid) == "jp"
    r = client.put(f"/accounts/{acc}/region", json={"region": "eu"},
                   headers={"authorization": f"Bearer {tok}"})
    assert r.status_code == 200, r.text
    assert r.json()["region"] == "eu"
    assert r.json()["providers"][0] == "mistral"
    assert loadouts.region_of(pid) == "eu"


def test_a_region_the_menu_does_not_know_is_refused(client):
    acc, tok = _account(client, "us")
    r = client.put(f"/accounts/{acc}/region", json={"region": "mars"},
                   headers={"authorization": f"Bearer {tok}"})
    assert r.status_code == 422
    r = client.post("/signup", json={"email": "m@example.com",
                                     "password": "longenough1",
                                     "region": "mars"})
    assert r.status_code == 422


def test_the_region_is_the_accounts_own_to_set(client):
    acc, _ = _account(client, "us")
    other, tok = _account(client, "ca")
    r = client.put(f"/accounts/{acc}/region", json={"region": "cn"},
                   headers={"authorization": f"Bearer {tok}"})
    assert r.status_code == 403


def test_the_american_lever_tapers_only_the_us_region(client, monkeypatch):
    acc, _ = _account(client, "us")
    pid = _profile_of(client, acc)
    monkeypatch.setenv("QRME_MODEL_POLICY", "american")
    us = loadouts.providers_for(pid)
    assert all(llm.origin_of(n) in ("US", "local", "any") for n in us)
    assert "deepseek" not in us
    # Another region is not bound by it.
    loadouts.set_region(acc, "eu")
    assert "mistral" in loadouts.providers_for(pid)


# --- the menu and the kitchen ------------------------------------------------

def test_the_menu_a_profile_reads_is_its_loadout(client):
    acc, _ = _account(client, "cn")
    pid = _profile_of(client, acc)
    menu = client.get("/models", params={"profile_id": pid}).json()
    assert menu["region"] == "cn"
    assert [p["name"] for p in menu["providers"]] == loadouts.providers_for(pid)
    assert all("origin" in p for p in menu["providers"])
    assert menu["video_providers"] == loadouts.video_providers_for(pid)


def test_a_provider_off_the_loadout_is_refused_with_the_menu(client):
    acc, _ = _account(client, "us")
    pid = _profile_of(client, acc)
    r = client.put(f"/profiles/{pid}/model", json={"provider": "zhipu"})
    assert r.status_code == 422
    assert "deepseek" in r.text                   # the menu it was offered
    r = client.put(f"/profiles/{pid}/model", json={"provider": "deepseek"})
    assert r.status_code == 200


# --- video, the same shape ---------------------------------------------------

def test_every_video_house_on_the_menu_is_on_the_shelf():
    for region, names in loadouts.VIDEO_LOADOUTS.items():
        for n in names:
            assert n in filming.PROVIDERS, f"{region} offers {n}, off the shelf"
            assert n in loadouts.VIDEO_ORIGINS, f"{n} names no origin"
    assert "higgsfield" in filming.PROVIDERS


def test_the_video_menu_follows_the_region(client, monkeypatch):
    acc, _ = _account(client, "us")
    pid = _profile_of(client, acc)
    us = loadouts.video_providers_for(pid)
    assert us[0] == "veo" and "higgsfield" in us and "kling" in us
    assert "vidu" not in us
    loadouts.set_region(acc, "cn")
    assert loadouts.video_providers_for(pid)[0] == "kling"
    loadouts.set_region(acc, "us")
    monkeypatch.setenv("QRME_MODEL_POLICY", "american")
    assert all(loadouts.VIDEO_ORIGINS[n] == "US"
               for n in loadouts.video_providers_for(pid))


def test_the_road_offers_the_menu_and_refuses_the_rest(client):
    acc, _ = _account(client, "us")
    pid = _profile_of(client, acc)
    road = client.get(f"/video/road/{pid}").json()
    assert road["providers"] == loadouts.video_providers_for(pid)
    r = client.post(f"/video/road/{pid}",
                    json={"road": "video", "daily_seconds": 60,
                          "provider": "vidu"})
    assert r.status_code == 422
    r = client.post(f"/video/road/{pid}",
                    json={"road": "video", "daily_seconds": 60,
                          "provider": "higgsfield"})
    assert r.status_code == 200 and r.json()["provider"] == "higgsfield"
    # Handing the choice back is never refused.
    r = client.post(f"/video/road/{pid}",
                    json={"road": "video", "provider": "none"})
    assert r.status_code == 200 and r.json()["provider_set"] is False
