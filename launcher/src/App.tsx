import { useEffect, useState } from "react";
import { api, getBase, setBase, type Ecosystem, type Health, type OperationEntry } from "./api";
import { useSession } from "./store";

const PRODUCTS = [
  { key: "qrme", name: "QRME", tag: "Synthetic profiles", accent: "#7b5cff", url: "http://localhost:5173" },
  { key: "jim", name: "JIM-mini", tag: "Guardian guidance", accent: "#43e08a", url: "http://localhost:5193" },
  { key: "pdi", name: "PDI", tag: "Encrypted vault", accent: "#38bdf8", url: "http://localhost:5183" },
] as const;

export function App() {
  const { session, setSession } = useSession();
  const [health, setHealth] = useState<Health | null>(null);
  const [name, setName] = useState("Dana");
  const [birthdate, setBirthdate] = useState("1984-06-01");
  const [base, setBaseInput] = useState(getBase());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [eco, setEco] = useState<Ecosystem | null>(null);
  const [ops, setOps] = useState<OperationEntry[] | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, [base]);

  async function signIn() {
    setBusy(true); setError(null);
    try {
      setSession(await api.session(name.trim(), birthdate));
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  const provisioned = (k: string) =>
    session?.products?.[k as keyof typeof session.products];

  async function buildEcosystem() {
    if (!session) return;
    setBusy(true); setError(null);
    try {
      setEco(await api.ecosystem(session));
      setOps((await api.operations(session)).entries);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  async function refreshOps() {
    if (!session) return;
    setBusy(true); setError(null);
    try { setOps((await api.operations(session)).entries); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  // The two joints the gateway wires in-process. False is "degraded", not
  // "down": the products still answer, but the care team / vault sealing
  // that ride the joint are off.
  const JOINTS = [
    { key: "jim_qrme" as const, name: "Care-team tandem",
      tag: "JIM reaches QRME's organizations" },
    { key: "qrme_pdi" as const, name: "Vault sealing",
      tag: "QRME's coordinations seal into PDI" },
  ];

  return (
    <div className="wrap">
      <header className="top">
        <span className="orb" />
        <div>
          <div className="title">Suite</div>
          <div className="sub">One login · one origin · three products</div>
        </div>
        <div className="spacer" />
        <span className={"origin " + (health ? "up" : "down")}>
          {health ? `● one origin · ${getBase()}` : "● gateway unreachable"}
        </span>
      </header>

      {!session ? (
        <div className="login">
          <h1>Unified sign-on</h1>
          <p className="muted">
            One identity, provisioned across QRME, JIM-mini, and PDI in a single call to the suite gateway.
          </p>
          <label>Name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
          <label>Birthdate<input type="date" value={birthdate} onChange={(e) => setBirthdate(e.target.value)} /></label>
          <label>Gateway URL
            <input value={base} onChange={(e) => { setBaseInput(e.target.value); setBase(e.target.value); }} />
          </label>
          {error && <div className="error">⚠ {error}</div>}
          <button className="primary" disabled={busy} onClick={signIn}>
            {busy ? "Signing in…" : "Sign in to the suite"}
          </button>
        </div>
      ) : (
        <div className="dash">
          <div className="hello">Signed in as <b>{session.identity}</b> — provisioned everywhere.</div>
          <div className="cards">
            {PRODUCTS.map((p) => {
              const live = health?.products?.[p.key]?.live;
              const id = provisioned(p.key);
              return (
                <div className="pcard" key={p.key} style={{ borderColor: p.accent }}>
                  <div className="pcard-top">
                    <span className="pdot" style={{ background: live ? "#43e08a" : "#6a6399" }} />
                    <div className="pname" style={{ color: p.accent }}>{p.name}</div>
                  </div>
                  <div className="ptag">{p.tag}</div>
                  <div className="pid">{id ? "identity provisioned ✓" : "not provisioned"}</div>
                  <a className="open" href={p.url} target="_blank" rel="noreferrer" style={{ borderColor: p.accent, color: p.accent }}>
                    Open console →
                  </a>
                </div>
              );
            })}
          </div>
          <div className="joints">
            {JOINTS.map((j) => {
              const wired = health?.tandems?.[j.key];
              return (
                <div className="joint" key={j.key}>
                  <span className="pdot" style={{ background: wired ? "#43e08a" : "#ffb84d" }} />
                  <div>
                    <div className="jname">{j.name}</div>
                    <div className="jtag">{wired ? j.tag : "not wired — runs degraded"}</div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="eco">
            {!eco ? (
              <>
                <p className="muted">
                  One press seeds your demo organization in QRME and links JIM's
                  care team to its first desk — a working ecosystem on your own
                  account. Pressing it again finds the same one.
                </p>
                <button className="primary" disabled={busy} onClick={buildEcosystem}>
                  {busy ? "Building…" : "Build my ecosystem"}
                </button>
              </>
            ) : (
              <div className="ecodone">
                <b>{eco.org.name}</b> — {eco.org.departments.map((d) => d.name).join(" · ")}
                <span className="jtag"> · care team {eco.care_team.linked ? "linked ✓" : "not linked"}</span>
              </div>
            )}
            {error && <div className="error">⚠ {error}</div>}
          </div>

          {ops !== null && (
            <div className="opsbox">
              <div className="opshead">
                <span>Operations — your coordinations as the vault recorded them</span>
                <button className="signout" disabled={busy} onClick={refreshOps}>Refresh</button>
              </div>
              {ops.length === 0 ? (
                <div className="jtag">Nothing sealed yet — coordinate from JIM's Care Team tab and it lands here.</div>
              ) : ops.map((o) => (
                <div className="oprow" key={o.key}>
                  <div className="opgoal">{o.goal || "(no goal recorded)"}</div>
                  <div className="jtag">{o.key} · {o.departments.filter(Boolean).join(", ")}</div>
                </div>
              ))}
            </div>
          )}

          <button className="signout" onClick={() => { setSession(null); setEco(null); setOps(null); }}>Sign out of the suite</button>
        </div>
      )}
    </div>
  );
}
