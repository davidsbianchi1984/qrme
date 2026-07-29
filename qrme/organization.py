"""The operational ecosystem: department agents that coordinate.

The PDI proposal promises, once the AI integration is switched on, "a
specialized AI assistant" per worker or department, and beyond individual
task support: "these AI systems will collaborate across departments, pulling
relevant data, offering smart suggestions, and coordinating efforts."

This module is that promise kept with the pieces the platform already has.
An organization belongs to an account; each department binds one profile
(its role-specific agent) with an optional **revocable vault grant** scoping
what that agent may read — the same grant machinery as claim-25 tasks, so
revoking a department's grant instantly stops its data pulls without
touching the org. A coordination takes one goal across departments: every
agent contributes from its own scoped material, in its own persona, and the
initiating department's agent composes the joint plan. The plan is
watermarked synthetic, and the whole record is sealed into the PDI vault
when the tandem is configured — the proposal's "same secure, private
network environment," honestly: coordination output is operational data and
belongs in the vault with the rest of it.

Coordinations are owner-facing operational insight, like simulations: never
distributed, so there is no moderation step — moderation gates what leaves
toward an audience.
"""

from __future__ import annotations

import json

from . import db, llm, persona, tasks, watermark


class OrganizationError(ValueError):
    """Refusal with a reason a person can read."""


def create(owner_id: str, name: str) -> dict:
    if not name.strip():
        raise OrganizationError("an organization needs a name")
    conn = db.connect()
    org_id = db.new_id("org")
    conn.execute(
        "INSERT INTO organizations (id, owner_id, name, created_at)"
        " VALUES (?,?,?,?)", (org_id, owner_id, name.strip(), db.utcnow()))
    conn.commit()
    return view(org_id)


def get(org_id: str) -> dict | None:
    row = db.connect().execute("SELECT * FROM organizations WHERE id=?",
                               (org_id,)).fetchone()
    return dict(row) if row else None


def view(org_id: str) -> dict:
    org = get(org_id)
    conn = db.connect()
    rows = conn.execute(
        "SELECT d.*, p.display_name FROM departments d"
        " JOIN profiles p ON p.id=d.profile_id"
        " WHERE d.org_id=? ORDER BY d.created_at, d.rowid",
        (org_id,)).fetchall()
    return {
        "id": org["id"], "name": org["name"], "created_at": org["created_at"],
        "departments": [{
            "id": r["id"], "name": r["name"], "role": r["role"],
            "profile_id": r["profile_id"], "agent": r["display_name"],
            "scoped": r["grant_id"] is not None,
        } for r in rows],
    }


def add_department(org: dict, name: str, role: str, profile: dict,
                   grant_token: str | None) -> dict:
    """Bind one agent to one department. The profile must belong to the same
    account as the organization — a department staffed by somebody else's
    agent would read the org's material on a stranger's model choices."""
    if profile["owner_id"] != org["owner_id"]:
        raise OrganizationError(
            "the department's agent must be a profile this organization's "
            "owner holds")
    if profile["adult_mode"]:
        raise OrganizationError("a rated profile cannot staff a department")
    grant_id = None
    if grant_token:
        grant = tasks._grant_for(profile["id"], grant_token)
        if grant is None or grant["revoked"]:
            raise OrganizationError("grant revoked or unknown")
        grant_id = grant["id"]
    conn = db.connect()
    dept_id = db.new_id("dep")
    try:
        conn.execute(
            "INSERT INTO departments (id, org_id, name, role, profile_id,"
            " grant_id, created_at) VALUES (?,?,?,?,?,?,?)",
            (dept_id, org["id"], name, role, profile["id"], grant_id,
             db.utcnow()))
    except Exception:
        raise OrganizationError(
            f"the organization already has a department named {name!r}")
    conn.commit()
    return view(org["id"])


def _scoped_items(department, pdi) -> list[dict]:
    """The department agent's readable material: its profile's sources,
    narrowed by its grant. A revoked grant reads as nothing — the pull
    stops, the department stays."""
    conn = db.connect()
    scope = None
    if department["grant_id"]:
        grant = conn.execute("SELECT * FROM grants WHERE id=?",
                             (department["grant_id"],)).fetchone()
        if grant is None or grant["revoked"]:
            return []
        scope = json.loads(grant["scope"])
    rows = conn.execute(
        "SELECT * FROM source_items WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC",
        (department["profile_id"],)).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        if scope is not None and scope != ["*"] and item["id"] not in scope:
            continue
        if item["pdi_key"] and pdi is not None:
            raw = pdi.get(item["pdi_key"])
            item["content"] = json.loads(raw)["content"] if raw else None
        items.append(item)
    return items


def coordinate(org: dict, goal: str, from_department_id: str,
               pdi=None, cloud=None) -> dict:
    """One goal, taken across the departments.

    Every department's agent contributes from its own scoped material; the
    initiating agent composes the joint plan from the contributions. Each
    step names how many items were pulled, never their raw content.
    """
    conn = db.connect()
    departments = [dict(r) for r in conn.execute(
        "SELECT * FROM departments WHERE org_id=?"
        " ORDER BY created_at, rowid", (org["id"],)).fetchall()]
    by_id = {d["id"]: d for d in departments}
    initiator = by_id.get(from_department_id)
    if initiator is None:
        raise OrganizationError("no such department in this organization")
    if len(departments) < 2:
        raise OrganizationError(
            "coordination takes at least two departments — add another "
            "before asking them to coordinate")

    contributions = []
    for dept in departments:
        profile = dict(conn.execute("SELECT * FROM profiles WHERE id=?",
                                    (dept["profile_id"],)).fetchone())
        items = _scoped_items(dept, pdi)
        system = persona.build_system_prompt(profile, None, None,
                                             sources=items)
        system += (f"\n\nYou are the {dept['name']} department's agent "
                   f"({dept['role']}) in {org['name']}. The organization's "
                   f"goal: {goal}. Offer your department's part — what you "
                   "see in your material, what you suggest, and what you "
                   "need from the other departments. Be concrete and brief.")
        content = llm.provider_for_profile(profile["id"], cloud=cloud).generate(
            system, [{"role": "user", "content": "Contribute your part."}])
        contributions.append({"department_id": dept["id"],
                              "department": dept["name"],
                              "content": content,
                              "items_read": len(items)})

    lead_profile = dict(conn.execute("SELECT * FROM profiles WHERE id=?",
                                     (initiator["profile_id"],)).fetchone())
    system = persona.build_system_prompt(lead_profile, None, None)
    system += (f"\n\nYou initiated a coordination across {org['name']} on: "
               f"{goal}. Each department has contributed:\n"
               + "\n".join(f"- {c['department']}: {c['content'][:400]}"
                           for c in contributions)
               + "\n\nCompose the joint plan: who does what, in what order, "
                 "and what each department hands the next.")
    plan = llm.provider_for_profile(
        lead_profile["id"], cloud=cloud).generate(
        system, [{"role": "user", "content": "Compose the joint plan."}])

    credential = watermark.stamp(lead_profile["id"], "coordination", plan)
    coordination_id = db.new_id("crd")
    pdi_key = None
    if pdi is not None:
        # Operational output belongs in the vault with the operational data.
        pdi_key = f"qrme/coordination/{coordination_id}"
        pdi.put(pdi_key, json.dumps({
            "org": org["name"], "goal": goal, "plan": plan,
            "contributions": contributions}))
    conn.execute(
        "INSERT INTO coordinations (id, org_id, goal, initiated_by, plan,"
        " status, watermark_id, pdi_key, created_at)"
        " VALUES (?,?,?,?,?,'completed',?,?,?)",
        (coordination_id, org["id"], goal, from_department_id, plan,
         credential["watermark_id"], pdi_key, db.utcnow()))
    for c in contributions:
        conn.execute(
            "INSERT INTO coordination_contributions (coordination_id,"
            " department_id, content, items_read) VALUES (?,?,?,?)",
            (coordination_id, c["department_id"], c["content"],
             c["items_read"]))
    conn.commit()
    return {
        "id": coordination_id, "org_id": org["id"], "goal": goal,
        "initiated_by": initiator["name"], "plan": plan,
        "contributions": contributions, "status": "completed",
        "watermark": credential,
        "sealed": pdi_key is not None, "pdi_key": pdi_key,
    }


def coordinations_for(org_id: str) -> list[dict]:
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM coordinations WHERE org_id=?"
        " ORDER BY created_at, rowid", (org_id,)).fetchall()
    out = []
    for row in rows:
        contribs = conn.execute(
            "SELECT c.department_id, c.items_read, d.name FROM"
            " coordination_contributions c JOIN departments d"
            " ON d.id=c.department_id WHERE c.coordination_id=?",
            (row["id"],)).fetchall()
        out.append({
            "id": row["id"], "goal": row["goal"], "plan": row["plan"],
            "status": row["status"], "sealed": row["pdi_key"] is not None,
            "created_at": row["created_at"],
            "departments": [{"name": c["name"],
                             "items_read": c["items_read"]}
                            for c in contribs],
        })
    return out


def seed_demo(owner_id: str) -> dict:
    """One press, a staffed organization — so the first meeting with the
    ecosystem is a working team, not an empty form.

    Everything created belongs to the caller's own account: two fresh
    enterprise agents with a little knowledge each and an all-scope grant,
    staffed to two desks. Nothing here touches the starter collection —
    those profiles belong to the platform, and a department may only be
    staffed by a profile its org's owner holds.
    """
    from . import auth, tasks as tasks_mod, terms

    conn = db.connect()
    agents = []
    for name, persona_text, role, know in (
        ("Workshop Agent",
         "A steady, practical foreman who knows the shop floor.",
         "runs the workshop",
         "Bench 2 is free Tuesdays; oak stock is low; the pew job needs "
         "two weekends."),
        ("Finance Agent",
         "A precise, kind bookkeeper who keeps everything square.",
         "keeps the books",
         "Materials budget this month: $1,400 committed, $600 free; "
         "invoices go out Fridays."),
    ):
        profile_id = db.new_id("prf")
        conn.execute(
            "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
            " demographics, sources, anonymous, adult_mode, interaction_scope,"
            " moderation_mode, aging_enabled, base_age, purpose, maturity,"
            " cloud_contribution, terms_version, terms_accepted_at, created_at)"
            " VALUES (?,?,?,?,?,'{}','[]',0,0,'reactive','auto',0,NULL,"
            " 'enterprise_agent','balanced',0,?,?,?)",
            (profile_id, owner_id, "fictional", name, persona_text,
             terms.TERMS_VERSION, db.utcnow(), db.utcnow()))
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
            (db.new_id("src"), profile_id, "knowledge", f"{name} notes",
             know, db.utcnow()))
        conn.commit()
        grant = tasks_mod.create_grant(profile_id, None)
        agents.append((profile_id, name, role, grant))

    org = create(owner_id, "The Demo Workshop")
    org_row = get(org["id"])
    for profile_id, name, role, grant in agents:
        profile = dict(conn.execute("SELECT * FROM profiles WHERE id=?",
                                    (profile_id,)).fetchone())
        add_department(org_row, name.replace(" Agent", ""), role, profile,
                       grant["token"])
    out = view(org["id"])
    out["note"] = ("a working demo team on your own account — coordinate a "
                   "goal, then revoke a grant and watch that desk's pulls "
                   "stop")
    out["owner_tokens"] = {name: auth.issue("owner", pid)
                          for pid, name, _, _ in agents}
    return out


def list_for(owner_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM organizations WHERE owner_id=?"
        " ORDER BY created_at, rowid", (owner_id,)).fetchall()
    return [view(r["id"]) for r in rows]
