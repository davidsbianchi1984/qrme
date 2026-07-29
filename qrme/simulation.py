"""Real-time simulation of the represented person, for predictive modeling.

Spec clause 1: the profile "may perform real-time simulations of the first
person's actions, workflows, and decision-making processes for predictive
modeling and operational insights." Clause 5: retained memory "may be
utilized for predictive modeling."

A run asks the persona — conditioned on its source material, its memory of a
chosen relationship, and its latent embedding — what the person would likely
decide and do in a scenario, and how. Two honesty rules shape everything
here:

- The narrative is a **prediction, watermarked as synthetic**, never the real
  person's word. The prompt says so and the stored row carries the credential.
- ``confidence`` reflects how much real evidence conditioned the run — source
  items, remembered turns, an embedding — not how sure the model sounds. A
  profile with no material honestly scores low however fluent its answer.

Runs are owner-only operational insight and are never distributed, which is
why there is no moderation step: moderation gates what leaves toward an
audience, and a simulation has none.
"""

from __future__ import annotations

import json

from . import adaptation, db, llm, persona, watermark

_HORIZON_LINES = {
    "immediate": "in the next moments",
    "short_term": "over the coming days or weeks",
    "long_term": "over months or years",
}


def _evidence(profile_id: str, interactor_id: str | None,
              sources: list[dict]) -> tuple[dict, float]:
    """What conditions the prediction, and the confidence it earns."""
    conn = db.connect()
    turns = 0
    embedding = None
    if interactor_id:
        turns = conn.execute(
            "SELECT COUNT(*) AS n FROM messages WHERE profile_id=?"
            " AND interactor_id=? AND status='approved'",
            (profile_id, interactor_id)).fetchone()["n"]
        embedding = adaptation.get(profile_id, interactor_id)
    basis = {
        "source_items": len(sources),
        "remembered_turns": turns,
        "latent_embedding": embedding["vector"] if embedding else None,
        "note": "confidence reflects the volume of real evidence behind the "
                "prediction, not the model's certainty",
    }
    confidence = (0.2
                  + 0.3 * min(1.0, len(sources) / 5)
                  + 0.25 * min(1.0, turns / 20)
                  + 0.15 * (1 if embedding else 0))
    return basis, round(min(confidence, 0.9), 2)


def run(profile: dict, scenario: str, horizon: str,
        interactor_id: str | None, pdi=None, cloud=None) -> dict:
    from .common import source_items
    profile_id = profile["id"]
    sources = source_items(profile_id, pdi)
    basis, confidence = _evidence(profile_id, interactor_id, sources)

    system = persona.build_system_prompt(profile, None, None, sources=sources)
    system += (
        "\n\nSimulation mode — predictive modeling, not conversation. "
        f"Model how {profile['display_name']} would act "
        f"{_HORIZON_LINES.get(horizon, horizon)} in this scenario:\n"
        f"{scenario}\n\n"
        "Give (1) the decision they would most likely make, (2) the concrete "
        "steps or workflow they would follow, and (3) why — grounded in who "
        "they are and what you know of their history. This is a synthetic "
        "prediction for operational insight; present it as what they would "
        "likely do, never as their actual word.")
    if interactor_id:
        attention = adaptation.attention_prompt(
            adaptation.get(profile_id, interactor_id))
        if attention:
            system += "\n\n" + attention
    narrative = llm.provider_for_profile(profile_id, cloud=cloud).generate(
        system, [{"role": "user", "content": "Run the simulation."}])

    # A prediction in someone's likeness is synthetic media: stamped.
    credential = watermark.stamp(profile_id, "simulation", narrative)
    conn = db.connect()
    sim_id = db.new_id("sim")
    conn.execute(
        "INSERT INTO simulations (id, profile_id, interactor_id, scenario,"
        " horizon, narrative, basis, confidence, watermark_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (sim_id, profile_id, interactor_id, scenario, horizon, narrative,
         json.dumps(basis), confidence, credential["watermark_id"],
         db.utcnow()))
    conn.commit()
    return {"id": sim_id, "scenario": scenario, "horizon": horizon,
            "narrative": narrative, "confidence": confidence, "basis": basis,
            "watermark": credential,
            "disclaimer": "a synthetic prediction of likely behavior, "
                          "not the person's actual word or plan"}


def list_runs(profile_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM simulations WHERE profile_id=?"
        " ORDER BY created_at, rowid", (profile_id,)).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["basis"] = json.loads(item["basis"])
        out.append(item)
    return out
