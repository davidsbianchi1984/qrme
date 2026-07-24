"""Federated pack registries: external mod storefronts on the marketplace.

Two partner registries publish packs into QRME alongside the local starter
collection — the same pattern the connected-apps catalog uses (represented
structurally; a live deployment would fetch each registry's feed):

- **Robotmods.net** — task mods for robot bodies (``audience: robot``)
- **LLMmods.com** — knowledge mods for LLM personas (``audience: profile``)

Syncing a registry imports its current catalog as ordinary knowledge packs
with ``origin`` set to the registry key and ``origin_url`` pointing at the
storefront, so every federated pack carries its source on the label. From
there nothing is special-cased: the same install/buy flow, the same
capability checks for robot mods, the same provenance counting, the same
uninstall. Syncing is idempotent — a pack whose (origin, title) is already
imported is skipped, so it is safe to run at every deploy:

    POST /packs/registries/{key}/sync
"""

from __future__ import annotations

import json

# registry key -> {name, url, audience, tagline, packs}
# Robot pack items: (task, title, [required capabilities], procedure).
# Profile pack items: (title, content).
REGISTRIES: dict[str, dict] = {
    "robotmods": {
        "name": "Robotmods.net",
        "url": "https://robotmods.net",
        "audience": "robot",
        "tagline": "Task mods for home robots — capability-matched to your "
                   "body.",
        "packs": [
            {"industry": "pets", "title": "Pet Care Mod", "price": 0.0,
             "blurb": "Daily pet routines for a humanoid or home robot.",
             "items": [
                 ("feed_pets", "Feed the pets", ["manipulation"],
                  "Dispense the measured portion into each bowl at the "
                  "scheduled times; never free-feed, and flag an untouched "
                  "bowl to the owner."),
                 ("litter_scan", "Litter & bowl check", ["vision"],
                  "Inspect litter areas and water bowls on the patrol route; "
                  "report what needs human attention rather than improvising."),
                 ("play_session", "Supervised play session", ["mobility"],
                  "Engage with the pet's registered toys only, gentle motion "
                  "profile, stop immediately if the animal shows stress."),
             ]},
            {"industry": "workshop", "title": "Workshop Assistant Mod",
             "price": 4.99,
             "blurb": "A steady extra pair of hands at the bench — never on "
                      "the tools.",
             "items": [
                 ("fetch_fastener", "Fetch fasteners & fittings",
                  ["manipulation", "vision"],
                  "Retrieve the named fastener size from the labeled bins; "
                  "confirm by reading the label, not by guessing."),
                 ("hold_light", "Hold the work light", ["manipulation"],
                  "Position and hold the light where directed and keep still; "
                  "never hold the workpiece itself while a tool is running."),
                 ("tidy_bench", "Tidy the bench", ["manipulation", "vision"],
                  "Return hand tools to their outlines when set down for five "
                  "minutes; power tools are never touched — flag them "
                  "instead."),
             ]},
        ],
    },
    "llmmods": {
        "name": "LLMmods.com",
        "url": "https://llmmods.com",
        "audience": "profile",
        "tagline": "Knowledge mods that make an LLM persona sharper in one "
                   "skill.",
        "packs": [
            {"industry": "negotiation", "title": "Negotiation Mod",
             "price": 0.0,
             "blurb": "Principled negotiation habits for any persona that "
                      "deals.",
             "items": [
                 ("Anchor with reasons",
                  "The first number sets the field, but only a justified "
                  "anchor holds; name the basis before the figure."),
                 ("Trade, don't concede",
                  "Every concession buys something specific in return — 'if "
                  "you can do X, I can do Y' keeps the exchange balanced."),
                 ("Know your walk-away",
                  "Decide the best alternative before the table, not at it; "
                  "a real option elsewhere is the quietest leverage there "
                  "is."),
             ]},
            {"industry": "public_speaking", "title": "Public Speaking Mod",
             "price": 3.49,
             "blurb": "Structure, delivery, and nerves — the working "
                      "speaker's toolkit.",
             "items": [
                 ("One message per talk",
                  "If the audience remembers a single sentence, choose that "
                  "sentence first and build every section to earn it."),
                 ("Pauses are punctuation",
                  "A held silence after a key line does what volume cannot; "
                  "rushing signals doubt, pausing signals command."),
                 ("Nerves are fuel",
                  "The body cannot tell stage fright from excitement — label "
                  "it excitement, slow the first thirty seconds, and let the "
                  "rehearsed opening carry you in."),
             ]},
        ],
    },
}


def registry_summaries() -> list[dict]:
    """Public listing of the federated registries with sync state."""
    from . import db

    conn = db.connect()
    out = []
    for key, reg in REGISTRIES.items():
        synced = conn.execute(
            "SELECT COUNT(*) AS n FROM knowledge_packs WHERE origin=?",
            (key,)).fetchone()["n"]
        out.append({"key": key, "name": reg["name"], "url": reg["url"],
                    "audience": reg["audience"], "tagline": reg["tagline"],
                    "available": len(reg["packs"]), "synced": synced})
    return out


def sync(key: str) -> dict | None:
    """Import a registry's catalog (idempotent by origin + title). Returns
    None for an unknown registry key."""
    from . import db
    from .models import ListingCreate
    from .routers.community import create_listing

    reg = REGISTRIES.get(key)
    if reg is None:
        return None
    conn = db.connect()
    created, skipped = [], []
    for pack in reg["packs"]:
        exists = conn.execute(
            "SELECT id FROM knowledge_packs WHERE origin=? AND title=?",
            (key, pack["title"])).fetchone()
        if exists:
            skipped.append(pack["title"])
            continue
        pack_id = db.new_id("pak")
        conn.execute(
            "INSERT INTO knowledge_packs (id, industry, audience, title,"
            " blurb, publisher, price, currency, origin, origin_url,"
            " created_at) VALUES (?,?,?,?,?,?,?,'USD',?,?,?)",
            (pack_id, pack["industry"], reg["audience"], pack["title"],
             pack["blurb"], reg["name"], pack["price"], key, reg["url"],
             db.utcnow()))
        for item in pack["items"]:
            if reg["audience"] == "robot":
                task, title, requires, procedure = item
                conn.execute(
                    "INSERT INTO pack_items (id, pack_id, title, content,"
                    " task, requires, created_at) VALUES (?,?,?,?,?,?,?)",
                    (db.new_id("pki"), pack_id, title, procedure, task,
                     json.dumps(requires), db.utcnow()))
            else:
                title, content = item
                conn.execute(
                    "INSERT INTO pack_items (id, pack_id, title, content,"
                    " created_at) VALUES (?,?,?,?,?)",
                    (db.new_id("pki"), pack_id, title, content, db.utcnow()))
        conn.commit()
        create_listing(ListingCreate(
            kind="expertise", title=pack["title"], blurb=pack["blurb"],
            tags=[pack["industry"].replace("_", "-"), "pack", key],
            area=pack["industry"], provider_name=reg["name"], business=True))
        created.append({"pack_id": pack_id, "title": pack["title"],
                        "price": pack["price"]})
    return {"registry": key, "name": reg["name"], "url": reg["url"],
            "created": len(created), "skipped": len(skipped),
            "packs": created}
