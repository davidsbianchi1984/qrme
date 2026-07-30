"""Role-specific interaction contexts (spec clauses 2 and 12).

Clause 2: adaptation "may extend to role-specific contexts, allowing the AI
profile to function as an advisor, collaborator, or operator based on the
user's interaction. The AI profile may autonomously interpret user prompts
to provide situationally relevant responses." Clause 12 carries the same
idea to synthesized persons — role-specific engagements across personal,
educational, and professional settings.

Two ways in, one honest record. The interactor can declare the role on the
chat turn (``role: "advisor"``), or leave it unset and let the profile read
the prompt itself — a transparent keyword reading, not a hidden model call,
so the inference is auditable and the reply's ``role_context`` says which
of the two happened. When neither declares nor infers, the profile simply
stays itself: a role is a lens the person reached for, never a costume
forced on every turn.

The frames deliberately shape *how* the profile works, not *who* it is —
persona, relationship, memory and moderation all still apply unchanged.
"""

from __future__ import annotations

ROLES = ("advisor", "collaborator", "operator")

# How each role works this turn. Written as instructions about posture,
# never as a new identity — the persona prompt above these lines still owns
# who is speaking.
_FRAMES = {
    "advisor": (
        "Role context for this turn — advisor: they came for counsel. Weigh "
        "the options they face, name the tradeoffs and risks plainly, and "
        "end with a clear recommendation and the reason it wins. Their "
        "decision stays theirs."),
    "collaborator": (
        "Role context for this turn — collaborator: you are working the "
        "problem together. Build on what they bring, contribute your own "
        "share of ideas, and leave an obvious next step one of you can pick "
        "up."),
    "operator": (
        "Role context for this turn — operator: they asked for the task "
        "done, not discussed. Produce the asked output precisely and "
        "completely, state any assumption you had to make, and keep "
        "commentary to a minimum."),
}

# Transparent inference: lowercase cue phrases per role, most hits wins,
# silence on a tie or no hits. Word-boundary-ish by keeping cues phrasal.
_CUES = {
    "advisor": ("should i", "what do you think", "recommend", "advice",
                "is it worth", "would you choose", "pros and cons",
                "what would you do"),
    "collaborator": ("let's", "lets ", "together", "brainstorm", "we could",
                     "help me think", "work with me", "bounce ideas"),
    "operator": ("draft ", "write me", "write a", "make me", "generate",
                 "put together", "prepare a", "compile", "translate this",
                 "summarize this"),
}


def frame(role: str) -> str:
    return _FRAMES[role]


def infer(message: str) -> str | None:
    """The autonomous reading of clause 2: which role does this prompt ask
    for? None when unclear — the profile then just stays itself."""
    text = (message or "").lower()
    scores = {role: sum(1 for cue in cues if cue in text)
              for role, cues in _CUES.items()}
    best = max(scores.values())
    if best == 0:
        return None
    leaders = [role for role, s in scores.items() if s == best]
    return leaders[0] if len(leaders) == 1 else None


def resolve(declared: str | None, message: str) -> dict | None:
    """The role context for this turn, with its provenance: declared by the
    interactor, or inferred from the prompt. None = no role — plain turn."""
    if declared:
        return {"role": declared, "how": "declared"}
    inferred = infer(message)
    if inferred:
        return {"role": inferred, "how": "inferred"}
    return None
