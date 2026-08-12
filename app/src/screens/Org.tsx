import { useEffect, useState } from "react";
import { api, CoordinationOut, OrgOut } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// The operational ecosystem (PDI proposal): departments staffed by your own
// profiles as role agents, coordinating on one goal — each pulls its own
// scoped material, the lead agent composes the joint plan. Staffing takes
// the profiles this account holds; a stranger's specialist enters only
// through a **lease** — licensed use, fee to its owner, revocable from the
// owner's side — never as ordinary staff on your material.
export function Org({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [orgs, setOrgs] = useState<OrgOut[]>([]);
  const [orgName, setOrgName] = useState("");
  const [deptName, setDeptName] = useState("");
  const [deptRole, setDeptRole] = useState("");
  const [deptProfile, setDeptProfile] = useState("");
  const [leaseProfile, setLeaseProfile] = useState("");
  const [leaseName, setLeaseName] = useState("");
  const [leaseRole, setLeaseRole] = useState("");
  const [goal, setGoal] = useState("");
  const [lead, setLead] = useState("");
  const [latest, setLatest] = useState<CoordinationOut | null>(null);
  const [history, setHistory] = useState<CoordinationOut[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

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
    }).catch((e) => setError(e));
  }
  useEffect(load, [token]);

  if (!token) {
    return <div className="screen"><p className="muted center">{tr("org.signin", lang)}</p></div>;
  }

  async function createOrg() {
    setBusy(true); setError(null);
    try { await api.createOrg(orgName.trim(), token!); setOrgName(""); load(); }
    catch (e) { setError(e); }
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
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  async function leaseIn() {
    if (!org) return;
    setBusy(true); setError(null);
    try {
      await api.leaseSpecialist(org.id, {
        profile_id: leaseProfile.trim(), name: leaseName.trim(),
        role: leaseRole.trim(),
      }, token!);
      setLeaseProfile(""); setLeaseName(""); setLeaseRole(""); load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  async function coordinate() {
    if (!org) return;
    setBusy(true); setError(null);
    try {
      const out = await api.coordinate(org.id,
        { goal: goal.trim(), from_department: lead }, token!);
      setLatest(out); setGoal(""); load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("org.title", lang)}</h2>
        <span className="muted small">{tr("org.pitch", lang)}</span>
      </header>

      {!org && (
        <div className="card">
          <h3>{tr("org.foundorg", lang)}</h3>
          <div className="row">
            <label>{tr("org.name", lang)}<input value={orgName} placeholder={tr("org.name.ph", lang)}
                              onChange={(e) => setOrgName(e.target.value)} /></label>
            <button className="primary" disabled={busy || !orgName.trim()} onClick={createOrg}>
              {tr("org.found", lang)}
            </button>
          </div>
          <p className="muted small">{tr("org.demopitch", lang)}</p>
          <button disabled={busy} onClick={async () => {
            setBusy(true); setError(null);
            try { await api.seedDemoOrg(token!); load(); }
            catch (e) { setError(e); }
            finally { setBusy(false); }
          }}>{tr("org.founddemo", lang)}</button>
        </div>
      )}

      {org && (
        <>
          <div className="card">
            <h3>{org.name}</h3>
            {org.departments.length === 0 && (
              <p className="muted small">{tr("org.nodepts", lang)}</p>
            )}
            {org.departments.map((d) => (
              <div key={d.id} className="friend-row">
                <b>{d.name}</b>
                <span className="muted small">
                  {fill(tr("org.roleagent", lang), { role: d.role, agent: d.agent })}
                </span>
                {d.scoped && <span className="tag">{tr("org.scoped", lang)}</span>}
                {d.leased && (
                  <span className="tag">
                    {d.lease_revoked ? tr("org.lease.revoked", lang)
                                     : tr("org.leased", lang)}
                  </span>
                )}
              </div>
            ))}
            <div className="row">
              <label>{tr("org.department", lang)}<input value={deptName} placeholder={tr("org.dept.ph", lang)}
                                      onChange={(e) => setDeptName(e.target.value)} /></label>
              <label>{tr("org.role", lang)}<input value={deptRole} placeholder={tr("org.role.ph", lang)}
                                onChange={(e) => setDeptRole(e.target.value)} /></label>
              <label>{tr("org.agentid", lang)}<input value={deptProfile} placeholder={tr("org.profile.ph", lang)}
                                            onChange={(e) => setDeptProfile(e.target.value)} /></label>
              <button className="primary" disabled={busy || !deptName.trim() || !deptRole.trim()}
                      onClick={addDept}>{tr("org.staff", lang)}</button>
            </div>
            <p className="muted small">{tr("org.lease.pitch", lang)}</p>
            <div className="row">
              <label>{tr("org.specialistid", lang)}<input value={leaseProfile} placeholder={tr("org.profile.ph", lang)}
                                            onChange={(e) => setLeaseProfile(e.target.value)} /></label>
              <label>{tr("org.department", lang)}<input value={leaseName} placeholder={tr("org.dept.ph", lang)}
                                      onChange={(e) => setLeaseName(e.target.value)} /></label>
              <label>{tr("org.role", lang)}<input value={leaseRole} placeholder={tr("org.role.ph", lang)}
                                onChange={(e) => setLeaseRole(e.target.value)} /></label>
              <button disabled={busy || !leaseProfile.trim() || !leaseName.trim() || !leaseRole.trim()}
                      onClick={leaseIn}>{tr("org.lease", lang)}</button>
            </div>
          </div>

          {org.departments.length >= 2 && (
            <div className="card">
              <h3>{tr("org.coordinate", lang)}</h3>
              <div className="row">
                <label>{tr("org.goal", lang)}<input value={goal} placeholder={tr("org.goal.ph", lang)}
                                  onChange={(e) => setGoal(e.target.value)} /></label>
                <label>{tr("org.lead", lang)}
                  <select value={lead} onChange={(e) => setLead(e.target.value)}>
                    {org.departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </label>
                <button className="primary" disabled={busy || !goal.trim()} onClick={coordinate}>
                  {busy ? tr("org.coordinating", lang) : tr("org.coordinate", lang)}
                </button>
              </div>
            </div>
          )}

          {latest && (
            <div className="card">
              <h3>
                {tr("org.plan", lang)}{" "}
                {latest.sealed && <span className="tag">{tr("org.sealedvault", lang)}</span>}
              </h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{latest.plan}</p>
              {(latest.contributions || []).map((c) => (
                <div key={c.department} className="friend-row">
                  <b>{c.department}</b>
                  <span className="muted small">
                    {fill(tr("org.items", lang), { n: c.items_read })}
                  </span>
                </div>
              ))}
            </div>
          )}

          {history.length > 0 && (
            <div className="card">
              <h3>{tr("org.past", lang)}</h3>
              {history.slice().reverse().map((c) => (
                <div key={c.id} className="friend-row">
                  <b>{c.goal.length > 50 ? c.goal.slice(0, 50) + "…" : c.goal}</b>
                  <span className="muted small">
                    {(c.departments || []).map((d) => d.name).join(" · ")}
                  </span>
                  {c.sealed && <span className="tag">{tr("org.sealed", lang)}</span>}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
