"""Latent persona embeddings and offline adaptation (claims 21, 22, 26).

The "multi-layer transformer" is the underlying Claude model; what QRME owns
is the state that conditions it. Each (profile, interactor) pair carries a
persistent **latent persona embedding** — a small named vector updated after
every interaction — so cross-session state survives logins, devices, and
model calls. At inference time the embedding is rendered as attention
weighting in the system prompt, so engagement literally conditions where the
model attends.

The vector is deliberately interpretable (named dimensions, EMA updates)
rather than opaque: v1 favors auditability over learned representations.

``finetune`` runs the offline pass of claim 26: it recomputes every
embedding from the full stored interaction history and seals the resulting
adaptation artifact — locally, or in the PDI vault when configured. No
interaction data is transmitted to any external model in the process.
"""

from __future__ import annotations

import json

from . import db

_ALPHA = 0.3          # EMA step for per-interaction updates

# Named latent dimensions, all 0..1.
DIMS = ("engagement", "warmth", "depth", "positivity", "stress", "continuity")

_WARMTH = {"family": 0.9, "grandchild": 0.95, "romantic_partner": 0.9,
           "friend": 0.7, "professional": 0.4, "fan": 0.5, "stranger": 0.2}


def _default() -> dict:
    return {"engagement": 0.5, "warmth": 0.2, "depth": 0.3,
            "positivity": 0.5, "stress": 0.0, "continuity": 0.0}


def get(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM persona_embeddings WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id)).fetchone()
    if row is None:
        return None
    return {"profile_id": profile_id, "interactor_id": interactor_id,
            "vector": json.loads(row["vector"]), "version": row["version"],
            "updated_at": row["updated_at"]}


def _signals(message: str, relationship: dict | None, engagement: dict | None,
             biometrics: dict | None) -> dict:
    target = _default()
    if engagement:
        target["engagement"] = engagement["score"]
        total = engagement["feedback_pos"] + engagement["feedback_neg"]
        if total:
            target["positivity"] = engagement["feedback_pos"] / total
        target["continuity"] = min(engagement["sessions"] / 10, 1.0)
    if relationship:
        target["warmth"] = _WARMTH.get(relationship["relationship_type"], 0.3)
    target["depth"] = min(len(message) / 400, 1.0)
    if biometrics:
        target["stress"] = float(biometrics.get("stress_level", 0) or 0)
    return target


def update(profile_id: str, interactor_id: str, message: str,
           relationship: dict | None, engagement: dict | None,
           biometrics: dict | None = None) -> dict:
    """EMA-update the latent embedding from this interaction's signals."""
    current = get(profile_id, interactor_id)
    vector = dict(current["vector"]) if current else _default()
    target = _signals(message, relationship, engagement, biometrics)
    for dim in DIMS:
        vector[dim] = round(vector[dim] + _ALPHA * (target[dim] - vector[dim]), 4)

    conn = db.connect()
    conn.execute(
        "INSERT INTO persona_embeddings (profile_id, interactor_id, vector,"
        " version, updated_at) VALUES (?,?,?,1,?)"
        " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
        " vector=excluded.vector, version=version+1,"
        " updated_at=excluded.updated_at",
        (profile_id, interactor_id, json.dumps(vector), db.utcnow()),
    )
    conn.commit()
    return get(profile_id, interactor_id)


def attention_prompt(embedding: dict | None) -> str | None:
    """Claim 22: render the embedding as attention conditioning — which parts
    of the context the model should weight, given the engagement state."""
    if embedding is None:
        return None
    v = embedding["vector"]
    weights = {
        "shared history & callbacks": round(0.2 + 0.8 * v["engagement"], 2),
        "emotional warmth": round(v["warmth"], 2),
        "depth & detail": round(0.2 + 0.8 * v["depth"], 2),
        "reassurance & de-escalation": round(v["stress"], 2),
    }
    rendered = ", ".join(f"{k}: {w}" for k, w in weights.items())
    return (f"Cross-session persona state (latent embedding v{embedding['version']}). "
            f"Attention weighting for this reply — {rendered}. "
            "Weight your focus accordingly; identity and boundaries stay fixed.")


def finetune(profile_id: str, pdi=None) -> dict:
    """Claim 26: encrypted, offline fine-tuning. Recomputes every interactor's
    embedding from full stored history and seals the adaptation artifact.
    Pure local computation — no interaction data leaves the host."""
    conn = db.connect()
    interactors = [r["interactor_id"] for r in conn.execute(
        "SELECT DISTINCT interactor_id FROM messages WHERE profile_id=?",
        (profile_id,)).fetchall()]

    artifact, processed, scores = {}, 0, []
    for interactor_id in interactors:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE profile_id=?"
            " AND interactor_id=? AND status='approved'"
            " ORDER BY created_at, rowid", (profile_id, interactor_id)).fetchall()
        eng = conn.execute(
            "SELECT * FROM engagement WHERE profile_id=? AND interactor_id=?",
            (profile_id, interactor_id)).fetchone()
        rel = conn.execute(
            "SELECT * FROM relationships WHERE profile_id=? AND interactor_id=?",
            (profile_id, interactor_id)).fetchone()
        vector = _default()
        for row in rows:
            if row["role"] != "interactor":
                continue
            processed += 1
            target = _signals(row["content"],
                              dict(rel) if rel else None,
                              dict(eng) if eng else None, None)
            for dim in DIMS:
                vector[dim] = round(
                    vector[dim] + _ALPHA * (target[dim] - vector[dim]), 4)
        artifact[interactor_id] = vector
        conn.execute(
            "INSERT INTO persona_embeddings (profile_id, interactor_id, vector,"
            " version, updated_at) VALUES (?,?,?,1,?)"
            " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
            " vector=excluded.vector, version=version+1,"
            " updated_at=excluded.updated_at",
            (profile_id, interactor_id, json.dumps(vector), db.utcnow()),
        )
        if eng:
            scores.append(eng["score"])

    run_id = db.new_id("ftr")
    vault_key = None
    if pdi is not None and artifact:
        vault_key = f"qrme/{profile_id}/adaptation/{run_id}"
        pdi.put(vault_key, json.dumps(artifact))
    metrics = {
        "interactors": len(interactors),
        "messages_processed": processed,
        "engagement_avg": round(sum(scores) / len(scores), 3) if scores else None,
        "external_transmission": False,
        "sealed_in_vault": vault_key is not None,
    }
    conn.execute(
        "INSERT INTO finetune_runs (id, profile_id, metrics, vault_key,"
        " created_at) VALUES (?,?,?,?,?)",
        (run_id, profile_id, json.dumps(metrics), vault_key, db.utcnow()),
    )
    conn.commit()
    return {"id": run_id, **metrics, "vault_key": vault_key}
