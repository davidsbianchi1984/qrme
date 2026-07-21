import { useEffect, useState } from "react";
import { api, getBase, setBase } from "../api";
import { useSession } from "../store";

export function Settings() {
  const { session, signOut } = useSession();
  const [base, setBaseInput] = useState(getBase());
  const [offline, setOffline] = useState<Record<string, unknown> | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.offlineStatus().then(setOffline).catch(() => setOffline(null));
  }, []);

  function save() {
    setBase(base);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
    api.offlineStatus().then(setOffline).catch((e) => setError((e as Error).message));
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Control Center</h2>
        <span className="muted small">you are in control</span>
      </header>

      <div className="card">
        <h3>API connection</h3>
        <label>
          Backend base URL
          <input value={base} onChange={(e) => setBaseInput(e.target.value)} />
        </label>
        <button className="primary" onClick={save}>{saved ? "Saved ✓" : "Save"}</button>
        {error && <div className="error">⚠ {error}</div>}
      </div>

      <div className="card">
        <h3>Offline status</h3>
        {offline ? (
          <pre className="mono">{JSON.stringify(offline, null, 2)}</pre>
        ) : (
          <div className="muted">Not reachable — is the backend running?</div>
        )}
      </div>

      <div className="card">
        <h3>Session</h3>
        <div className="muted small">Profile: {session.profileId}</div>
        <button className="danger" onClick={signOut}>Sign out &amp; end session</button>
      </div>
    </div>
  );
}
