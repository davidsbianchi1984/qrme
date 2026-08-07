"""Owner-authorized workflow delegation — letting somebody else start one.

``qrme/workflows.py`` runs a plan (`research → draft → review → send →
confirm`) in character, carrying memory between phases and surviving across
sessions. Every route that reaches it is ``require_owner``, which is correct
for the owner's own console and wrong for the case this module exists for:
**JIM-mini's Guardian noticing something and handing the work to a QRME
specialist**, where the caller is an interactor in a conversation, not the
profile's owner.

The obvious fix — relax the workflow routes to accept an interactor — is the
wrong one, for a reason worth stating plainly.

**A workflow is not a chat turn.** ``POST /profiles/{id}/chat`` composes one
reply and moderates it. A workflow runs several phases unattended, and its
`research` phase reads the profile's **vaulted source material**. Worse,
``workflows._scoped_items`` treats a missing grant as scope ``["*"]`` — *all of
it*. A chat turn that anyone may start is a considered decision; an
unattended multi-phase read over everything the owner ever vaulted, startable
by anyone who can reach the endpoint, is not the same decision at a larger
size. It is a different one.

So delegation is **off until an owner turns it on**, and turning it on means
saying what may be delegated:

* **No policy means no delegation.** Absent row is 403, not an empty default.
  A capability that appears only when somebody deliberately asks for it.
* **The phases are named by the owner**, and a delegated request may only ask
  for a subset. Nobody widens their own envelope.
* **A grant is mandatory the moment `research` is delegable.** This is the
  whole point: the owner names the grant, the grant names the source items,
  and the ``["*"]`` default can never be reached down this path. Delegating
  research without a grant is refused at write time (422), where the owner is
  present to read the error — not at 3am inside somebody else's workflow.
* **The caller must already be in conversation with the profile** — at least
  one exchanged message. Not a *relationship* row: those are owner-set, and
  requiring one would mean an owner hand-naming every caller before any
  handoff could happen, which for JIM's tandem specialists is a per-user
  deployment chore rather than a safety property. The policy above is the
  authorization; this check only rules out a stranger who has the profile's
  id and nothing else.

Only the interactor who started a delegated workflow may read or advance it,
and they can reach it *only* through the delegated routes — the owner's
workflow routes stay owner-only. The two surfaces never merge.

`send` is delegable, and that is deliberate rather than an oversight: the
phase produces the finished deliverable, it does not transmit anything. There
is no code path from a workflow phase to an outbound message.
"""

from __future__ import annotations

import json

from . import db, workflows

# Phases an owner may put in a delegation policy. Identical to
# ``workflows.PHASES`` today; named separately so narrowing what is delegable
# never silently narrows what an owner can run themselves.
DELEGABLE = ("research", "draft", "review", "send", "confirm")


class DelegationError(ValueError):
    """A delegated request the policy does not permit.

    Raised on the *request* path, where the caller is a machine that must be
    told no in a way it can act on — never as a way of reporting a policy the
    owner wrote badly, which is caught at write time instead.
    """


def set_policy(profile_id: str, phases: list[str], grant_id: str | None,
               enabled: bool = True) -> dict:
    """Declare what a delegated caller may run. Owner-only at the route.

    Validation happens **here, on write**, so a policy that cannot work is
    refused while the owner is looking at it.
    """
    unknown = [p for p in phases if p not in DELEGABLE]
    if unknown:
        raise ValueError(f"not delegable: {', '.join(unknown)}")
    if not phases:
        raise ValueError("a delegation policy needs at least one phase")
    if "research" in phases and grant_id is None:
        raise ValueError(
            "delegating `research` requires a grant: without one the phase "
            "reads every source item on the profile")

    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO delegation_policies"
        " (profile_id, phases, grant_id, enabled, created_at, updated_at)"
        " VALUES (?,?,?,?,?,?)"
        " ON CONFLICT(profile_id) DO UPDATE SET"
        " phases=excluded.phases, grant_id=excluded.grant_id,"
        " enabled=excluded.enabled, updated_at=excluded.updated_at",
        (profile_id, json.dumps(phases), grant_id, int(enabled), now, now),
    )
    conn.commit()
    return get_policy(profile_id)


def get_policy(profile_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM delegation_policies WHERE profile_id=?",
        (profile_id,)).fetchone()
    if row is None:
        return None
    p = dict(row)
    p["phases"] = json.loads(p["phases"])
    p["enabled"] = bool(p["enabled"])
    return p


def offer(profile_id: str) -> dict:
    """What a caller may ask for — safe to show an unauthenticated reader.

    Deliberately omits ``grant_id``. Which source items the owner scoped is
    the owner's business; the caller only needs to know the shape of the
    request that will be accepted.
    """
    policy = get_policy(profile_id)
    # `delegable` is the vocabulary; `phases` is what this owner has chosen
    # from it. The console rendered its toggles from `phases` and so had
    # nothing to draw whenever delegation was off — which is every profile
    # before the first time it is switched on, so it could never be switched
    # on. A capability advertisement has to say what is possible, not only
    # what is already true.
    if policy is None or not policy["enabled"]:
        return {"delegation": False, "phases": [], "delegable": list(DELEGABLE)}
    return {"delegation": True, "phases": policy["phases"],
            "delegable": list(DELEGABLE)}


def start(profile_id: str, interactor_id: str, goal: str,
          plan: list[str] | None) -> dict:
    """Start a workflow on somebody else's behalf, inside the owner's policy.

    The plan defaults to the whole policy rather than to
    ``workflows.DEFAULT_PLAN`` — a delegated caller that names no plan gets
    what the owner allowed, never the product's default.
    """
    policy = get_policy(profile_id)
    if policy is None or not policy["enabled"]:
        raise DelegationError(
            "this profile does not accept delegated workflows")

    plan = plan or list(policy["phases"])
    outside = [p for p in plan if p not in policy["phases"]]
    if outside:
        raise DelegationError(
            f"policy does not permit: {', '.join(outside)}; "
            f"permitted: {', '.join(policy['phases'])}")

    wf = workflows.create(profile_id, goal, plan, policy["grant_id"])
    conn = db.connect()
    conn.execute(
        "INSERT INTO delegated_workflows"
        " (workflow_id, profile_id, interactor_id, created_at)"
        " VALUES (?,?,?,?)",
        (wf["id"], profile_id, interactor_id, db.utcnow()),
    )
    conn.commit()
    return {**wf, "delegated_to": interactor_id}


def in_conversation(profile_id: str, interactor_id: str) -> bool:
    """Whether these two have actually exchanged anything.

    Deliberately the ``messages`` table rather than ``relationships``: a
    relationship is something the *owner* sets, so requiring one would gate
    every delegated handoff behind an owner action per caller. What this rules
    out is a stranger holding nothing but the profile's id.
    """
    row = db.connect().execute(
        "SELECT 1 FROM messages WHERE profile_id=? AND interactor_id=? LIMIT 1",
        (profile_id, interactor_id)).fetchone()
    return row is not None


def started_by(profile_id: str, workflow_id: str) -> str | None:
    """The interactor who started this delegated workflow, or None if it was
    not delegated at all — which is how an owner's own workflow stays
    unreachable from the delegated routes."""
    row = db.connect().execute(
        "SELECT interactor_id FROM delegated_workflows"
        " WHERE workflow_id=? AND profile_id=?",
        (workflow_id, profile_id)).fetchone()
    return row["interactor_id"] if row else None


def list_for(profile_id: str, interactor_id: str) -> list[dict]:
    """The delegated workflows this interactor started on this profile."""
    rows = db.connect().execute(
        "SELECT workflow_id FROM delegated_workflows"
        " WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at, rowid", (profile_id, interactor_id)).fetchall()
    out = []
    for r in rows:
        wf = workflows.get(profile_id, r["workflow_id"])
        if wf is not None:
            out.append({**wf, "delegated_to": interactor_id})
    return out
