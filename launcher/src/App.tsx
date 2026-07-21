import { useEffect, useState } from "react";
import { api, getBase, setBase, type Health } from "./api";
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
          <button className="signout" onClick={() => setSession(null)}>Sign out of the suite</button>
        </div>
      )}
    </div>
  );
}
