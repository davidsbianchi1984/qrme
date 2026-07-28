import { useEffect, useState } from "react";
import { api, getBase, getLlmKey, setBase, setLlmKey, type PairInfo } from "../api";
import { useSession } from "../store";

export function Settings() {
  const { session, signOut } = useSession();
  const [base, setBaseInput] = useState(getBase());
  const [llmKey, setLlmKeyInput] = useState(getLlmKey());
  const [keySaved, setKeySaved] = useState(false);
  const [offline, setOffline] = useState<Record<string, unknown> | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pair, setPair] = useState<PairInfo | null>(null);

  useEffect(() => {
    api.offlineStatus().then(setOffline).catch(() => setOffline(null));
    api.pair().then(setPair).catch(() => setPair(null));
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
        <h3>Your model API key</h3>
        <p className="muted small">
          Paste your own key (Anthropic <code>sk-ant-…</code>, or OpenAI / xAI /
          Gemini for those providers) and your profiles' replies run on your
          credential. It stays on this device and rides only your own requests —
          the server never stores it. Leave it empty to use whatever key the
          deployment lends.
        </p>
        <label>API key
          <input type="password" value={llmKey} placeholder="sk-…"
                 onChange={(e) => setLlmKeyInput(e.target.value)} />
        </label>
        <button className="primary" onClick={() => {
          setLlmKey(llmKey); setKeySaved(true); setTimeout(() => setKeySaved(false), 1500);
        }}>{keySaved ? "Saved ✓" : llmKey.trim() ? "Save key" : "Clear key"}</button>
      </div>

      <div className="card">
        <h3>Offline status</h3>
        {offline ? (
          <pre className="mono">{JSON.stringify(offline, null, 2)}</pre>
        ) : (
          <div className="muted">Not reachable — is the backend running?</div>
        )}
      </div>

      {pair && (
        <div className="card">
          <h3>Open on your phone</h3>
          <p className="muted small">{pair.note}</p>
          <div className="pair">
            <img className="pair-qr" src={getBase() + pair.qr_svg} alt="QR code for the studio URL on this network" />
            <div>
              <div className="mono pair-url">{pair.console_url}</div>
              <ol className="pair-steps">{pair.how.map((s) => <li key={s}>{s}</li>)}</ol>
            </div>
          </div>
        </div>
      )}
      <div className="card">
        <h3>Session</h3>
        <div className="muted small">Profile: {session.profileId}</div>
        <button className="danger" onClick={signOut}>Sign out &amp; end session</button>
      </div>
    </div>
  );
}
