import { useEffect, useState } from "react";
import { api, CoordinationOut, OrgOut } from "../api";
import { useSession } from "../store";

// The operational ecosystem (PDI proposal): departments staffed by your own
// profiles as role agents, coordinating on one goal — each pulls its own
// scoped material, the lead agent composes the joint plan. Candidate agents
// are the profiles this account holds plus the marketplace is NOT offered:
// a department staffed by a stranger's agent would read your material on
// somebody else's model choices, and the backend refuses it anyway.
export function Org() {
  const { session } = useSession();
  const [orgs, setOrgs] = useState<OrgOut[]>([]);
  const [orgName, setOrgName] = useState("");
  const [deptName, setDeptName] = useState("");
  const [deptRole, setDeptRole] = useState("");
  const [deptProfile, setDeptProfile] = useState("");
  const [goal, setGoal] = useState("");
  const [lead, setLead] = useState("");
  const [latest, setLatest] = useState<CoordinationOut | null>(null);
  const [history, setHistory] = useState<CoordinationOut[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = session.ownerToken;
  const org = orgs[0];   // one org per account covers the console's needs

  function load() {
    if (!token) return;
    api.listOrgs(token).then((o) => {
      setOrgs(o);
      if (o[0]?.departments.length && !lead) setLead(o[0].departments[0].id);
      if (o[0]) {
        api.listCoordinations(o[0].id, token)
          .then(setHistory).catch(() => setHistory([]));
      }
    }).catch((e) => setError((e as Error).message));
  }
  useEffect(load, [token]);

  if (!token) {
    return <div className="screen"><p className="muted center">Sign in first.</p></div>;
  }

  async function createOrg() {
    setBusy(true); setError(null);
    try { await api.createOrg(orgName.trim(), token!); setOrgName(""); load(); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function addDept() {
    if (!org) return;
    setBusy(true); setError(null);
    try {
      await api.addDepartment(org.id, {
        name: deptName.trim(), role: deptRole.trim(),
        profile_id: deptProfile.trim() || session.profileId!,
      }, token!);
      setDeptName(""); setDeptRole(""); setDeptProfile(""); load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function coordinate() {
    if (!org) return;
    setBusy(true); setError(null);
    try {
      const out = await api.coordinate(org.id,
        { goal: goal.trim(), from_department: lead }, token!);
      setLatest(out); setGoal(""); load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>The Ecosystem</h2>
        <span className="muted small">departments that coordinate — your agents, your material, one joint plan</span>
      </header>

      {!org && (
        <div className="card">
          <h3>Found an organization</h3>
          <div className="row">
            <label>Name<input value={orgName} placeholder="e.g. Bianchi & Sons"
                              onChange={(e) => setOrgName(e.target.value)} /></label>
            <button className="primary" disabled={busy || !orgName.trim()} onClick={createOrg}>Found</button>
          </div>
        </div>
      )}

      {org && (
        <>
          <div className="card">
            <h3>{org.name}</h3>
            {org.departments.length === 0 && (
              <p className="muted small">No departments yet — staff the first desk below.</p>
            )}
            {org.departments.map((d) => (
              <div key={d.id} className="friend-row">
                <b>{d.name}</b>
                <span className="muted small">{d.role} · agent: {d.agent}</span>
                {d.scoped && <span className="tag">scoped</span>}
              </div>
            ))}
            <div className="row">
              <label>Department<input value={deptName} placeholder="Finance"
                                      onChange={(e) => setDeptName(e.target.value)} /></label>
              <label>Role<input value={deptRole} placeholder="keeps the books"
                                onChange={(e) => setDeptRole(e.target.value)} /></label>
              <label>Agent profile id<input value={deptProfile} placeholder="(this profile)"
                                            onChange={(e) => setDeptProfile(e.target.value)} /></label>
              <button className="primary" disabled={busy || !deptName.trim() || !deptRole.trim()}
                      onClick={addDept}>Staff</button>
            </div>
          </div>

          {org.departments.length >= 2 && (
            <div className="card">
              <h3>Coordinate</h3>
              <div className="row">
                <label>Goal<input value={goal} placeholder="quote and schedule the restoration"
                                  onChange={(e) => setGoal(e.target.value)} /></label>
                <label>Lead
                  <select value={lead} onChange={(e) => setLead(e.target.value)}>
                    {org.departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </label>
                <button className="primary" disabled={busy || !goal.trim()} onClick={coordinate}>
                  {busy ? "Coordinating…" : "Coordinate"}
                </button>
              </div>
            </div>
          )}

          {latest && (
            <div className="card">
              <h3>The joint plan {latest.sealed && <span className="tag">sealed to vault</span>}</h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{latest.plan}</p>
              {(latest.contributions || []).map((c) => (
                <div key={c.department} className="friend-row">
                  <b>{c.department}</b>
                  <span className="muted small">{c.items_read} item(s) pulled</span>
                </div>
              ))}
            </div>
          )}

          {history.length > 0 && (
            <div className="card">
              <h3>Past coordinations</h3>
              {history.slice().reverse().map((c) => (
                <div key={c.id} className="friend-row">
                  <b>{c.goal.length > 50 ? c.goal.slice(0, 50) + "…" : c.goal}</b>
                  <span className="muted small">
                    {(c.departments || []).map((d) => d.name).join(" · ")}
                  </span>
                  {c.sealed && <span className="tag">sealed</span>}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
