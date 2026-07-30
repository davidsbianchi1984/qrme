"""Every option the backend offers, the backend must accept.

A catalog endpoint is a menu. The console and the three shells render it
directly — a language picker, a provider list, a robot catalog — so whatever it
lists is what a user can choose. If the endpoint that *consumes* the choice
refuses one of those values, the user picks it from a dropdown and meets an
error for doing exactly what they were offered.

That is the Wall bug's shape once more: the request routes perfectly, and the
refusal happens inside the handler, after dispatch. Both route guards in this
directory say plainly that they cannot see that far. This one can, because it
stops reading source and sends the request.

What it does not cover: a choice the client invents rather than reads from a
catalog, and a refusal that depends on state this fixture does not set up (a
plan gate, a quota, a moderation verdict). Those need their own tests, and
several have them.
"""

from __future__ import annotations

import pytest


def _accepted(response) -> bool:
    """A 2xx, or a refusal that is clearly about something other than the value.

    409 is the one status that is not evidence of a bad vocabulary: it means the
    server understood the value and objected to the state — already connected,
    already bound. Anything in the 4xx range that names the *value* is what this
    test is looking for.
    """
    return response.status_code < 400 or response.status_code == 409


def _check(label, offered, send):
    assert offered, f"{label}: the catalog offered nothing, so nothing was checked"
    refused = []
    for value in offered:
        response = send(value)
        if not _accepted(response):
            refused.append(f"{value!r} -> {response.status_code} "
                           f"{response.text[:120]}")
    assert not refused, (
        f"{label}: the backend offers these and then refuses them:\n  "
        + "\n  ".join(refused)
        + "\n(a value the user picked from a list the server itself supplied)"
    )


@pytest.mark.parametrize("mode", ["pre", "on_demand"])
def test_every_offered_language_can_be_set(client, profile_id, mode):
    """Both delivery modes, because the pair is validated together.

    A language accepted in one mode and refused in the other would be invisible
    to a test that only tried the default.
    """
    offered = [row["code"] for row in client.get("/languages").json()["languages"]]
    _check(
        f"language ({mode})", offered,
        lambda code: client.put(f"/profiles/{profile_id}/language",
                                json={"language": code, "mode": mode}),
    )


def test_every_offered_language_can_be_translated_into(client, profile_id):
    """The same menu, a different kitchen.

    `/languages` feeds both the profile's own language and the Translate tool.
    Two consumers of one list is exactly where a vocabulary drifts, so both are
    asked.
    """
    offered = [row["code"] for row in client.get("/languages").json()["languages"]]
    _check(
        "translate target", offered,
        lambda code: client.post(f"/profiles/{profile_id}/translate",
                                 json={"text": "hello", "target": code}),
    )


def test_every_dial_the_server_describes_can_be_set(client, profile_id):
    """The steering screen renders whatever this endpoint returns.

    A dial described but not settable is a slider that throws when moved.
    """
    described = [d["name"] for d in
                 client.get(f"/profiles/{profile_id}/steering").json()["dials"]]
    _check(
        "steering dial", described,
        lambda name: client.put(f"/profiles/{profile_id}/steering",
                                json={"dials": {name: 50}}),
    )


def test_every_provider_on_the_menu_can_be_chosen(client, profile_id):
    """Including the ones with no key configured.

    Choosing an unconfigured provider is allowed on purpose — the profile
    records the preference and the runtime falls back with a warning, so the
    owner can set the choice before pasting the key. A refusal here would make
    the provider tiles unusable until a key existed.
    """
    providers = client.get("/models").json()["providers"]
    _check(
        "provider", [(p["name"], p["model"]) for p in providers],
        lambda pair: client.put(f"/profiles/{profile_id}/model",
                                json={"provider": pair[0], "model": pair[1]}),
    )


def test_every_robot_in_the_catalog_can_be_bound(client, profile_id):
    catalog = client.get("/robotics/catalog").json()["robots"]
    _check(
        "robot", [r["model"] for r in catalog],
        lambda model: client.post(f"/profiles/{profile_id}/robots",
                                  json={"model": model}),
    )


def test_every_connector_in_the_catalog_can_be_connected(client, profile_id):
    """Provider and app together, which is how the catalog is keyed.

    `/apps/{cid}` takes a *connection* id rather than a catalog name — you
    connect first and collect afterwards — so the catalog's own contract is with
    this endpoint, not with collect.
    """
    catalog = client.get("/connectors/catalog").json()["providers"]
    pairs = [(p["provider"], app["app"])
             for p in catalog for app in (p.get("apps") or [])]
    _check(
        "connector", pairs,
        lambda pair: client.post(f"/profiles/{profile_id}/apps",
                                 json={"provider": pair[0], "app": pair[1]}),
    )


def test_every_pack_registry_listed_can_be_synced(client):
    registries = client.get("/packs/registries").json()
    _check(
        "pack registry", [r["key"] for r in registries],
        lambda key: client.post(f"/packs/registries/{key}/sync"),
    )
