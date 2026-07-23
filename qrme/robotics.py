"""Robotics catalog — the physical bodies a profile can inhabit.

A registry of supported robot platforms, from full humanoids to home robots to
autonomous vacuums. Mirrors the connected-apps catalog pattern (``catalog.py``):
a static, auditable table the routers validate against, shared verbatim across
QRME, JIM-mini, and PDI so a robot bound in one product means the same thing in
the others.

``llm_capable`` marks platforms that can run an onboard language model; the
binding then records *which* provider (from the ``qrme.llm`` registry) the
robot is loaded with, so the same persona speaks through the same model
wherever it is embodied.

Commands are validated against a per-kind allowlist — a vacuum cannot be told
to "fetch", and nothing outside the list ever reaches a robot.
"""

from __future__ import annotations

# (key, label, maker, kind, capabilities, llm_capable)
_ROWS: list[tuple[str, str, str, str, list[str], bool]] = [
    ("isaac_1", "Isaac 1", "Weave Robotics", "home_robot",
     ["mobility", "manipulation", "voice", "vision", "tidying"], True),
    ("neo", "NEO", "1X Technologies", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "chores"], True),
    ("u1_lite", "UWorld U1 Lite", "UBTech Robotics", "humanoid",
     ["mobility", "voice", "vision"], True),
    ("u1_pro", "UWorld U1 Pro", "UBTech Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision"], True),
    ("u1_ultra", "UWorld U1 Ultra", "UBTech Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "chores"], True),
    ("memo", "Memo", "Sunday Robotics", "home_robot",
     ["mobility", "manipulation", "voice", "vision", "tidying"], True),
    ("saros_20", "Saros 20", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "mop", "camera_patrol"], True),
    ("saros_20_sonic", "Saros 20 Sonic", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "sonic_mop", "camera_patrol"], True),
    ("qrevo_curv_2_flow", "Qrevo Curv 2 Flow", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "mop"], False),
]

BY_KEY: dict[str, dict] = {
    key: {"model": key, "label": label, "maker": maker, "kind": kind,
          "capabilities": caps, "llm_capable": llm}
    for key, label, maker, kind, caps, llm in _ROWS
}

# What each kind of body may be told to do. Everything else is refused.
COMMANDS: dict[str, list[str]] = {
    "humanoid": ["say", "come_here", "follow", "fetch", "tidy", "patrol",
                 "dock", "stop"],
    "home_robot": ["say", "come_here", "follow", "fetch", "tidy", "patrol",
                   "dock", "stop"],
    "vacuum": ["clean", "spot_clean", "patrol", "dock", "locate", "stop"],
}

# How a robot kind maps onto the existing embodiment kinds.
EMBODIMENT_KIND = {"humanoid": "humanoid", "home_robot": "robot",
                   "vacuum": "robot"}


def catalog() -> dict:
    """The full registry, grouped by maker, for the catalog endpoint."""
    makers: dict[str, list[dict]] = {}
    for row in BY_KEY.values():
        makers.setdefault(row["maker"], []).append(row)
    return {"robots": list(BY_KEY.values()), "by_maker": makers,
            "commands": COMMANDS}


def get(model: str) -> dict | None:
    return BY_KEY.get(model)


def allowed_commands(model: str) -> list[str]:
    spec = BY_KEY.get(model)
    return COMMANDS.get(spec["kind"], []) if spec else []
