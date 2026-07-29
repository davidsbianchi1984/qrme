import { useEffect, useState } from "react";
import { accountApi, api, getBase, getLlmKey, setBase, setLlmKey, type PairInfo } from "../api";
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

      <MailPanel />

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


// Where this deployment sends mail through. Until a host is set here (or in
// the environment), no verification email can reach anybody — the message
// goes to the server's log instead, which is why local signup does not wait
// for one. Fill this in and the emails become real.
function MailPanel() {
  const [cfg, setCfg] = useState<Awaited<ReturnType<typeof accountApi.getMailSettings>> | null>(null);
  const [host, setHost] = useState("");
  const [port, setPort] = useState(587);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [sender, setSender] = useState("");
  const [publicUrl, setPublicUrl] = useState("");
  const [testTo, setTestTo] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    accountApi.getMailSettings().then((c) => {
      setCfg(c);
      setHost(c.host || ""); setPort(c.port || 587);
      setUsername(c.username || ""); setSender(c.sender || "");
      setPublicUrl(c.public_url || ""); setTestTo(c.username || "");
    }).catch(() => setCfg(null));
  }
  useEffect(load, []);

  async function run(fn: () => Promise<unknown>, ok: string) {
    setBusy(true); setError(null); setNote(null);
    try { await fn(); setNote(ok); load(); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>Email delivery</h3>
      <p className="muted small">
        {cfg?.transport === "smtp"
          ? <>Mail goes out through <b>{cfg.host}</b>{cfg.source === "environment" && " (set by environment variables)"}. New accounts must verify by email.</>
          : <>No mail server configured, so <b>nothing can be emailed</b> — verification messages are written to this app's log and signup on this machine simply goes straight in. Point it at a mail account below to send real verification links. For Gmail, turn on 2-Step Verification and create an <b>App password</b>; paste that here, not your normal password.</>}
      </p>
      {cfg?.source !== "environment" && (<>
        <div className="row">
          <label>Mail server<input value={host} placeholder="smtp.gmail.com" onChange={(e) => setHost(e.target.value)} /></label>
          <label>Port<input type="number" value={port} onChange={(e) => setPort(Number(e.target.value))} /></label>
        </div>
        <label>Username<input value={username} placeholder="you@gmail.com" onChange={(e) => setUsername(e.target.value)} /></label>
        <label>Password {cfg?.password_set && <span className="muted small">(saved — type to replace)</span>}
          <input type="password" value={password} placeholder="app password" onChange={(e) => setPassword(e.target.value)} />
        </label>
        <label>From address<input value={sender} placeholder="you@gmail.com" onChange={(e) => setSender(e.target.value)} /></label>
        <label>Link address <span className="muted small">— what verification links point at</span>
          <input value={publicUrl} placeholder="http://127.0.0.1:8000" onChange={(e) => setPublicUrl(e.target.value)} />
        </label>
        <div className="actions">
          <button className="primary" disabled={busy || !host.trim()}
                  onClick={() => run(() => accountApi.saveMailSettings({
                    host, port, username, password: password || undefined,
                    sender, public_url: publicUrl }), "Saved.")}>
            {busy ? "Saving…" : "Save mail settings"}
          </button>
          {cfg?.transport === "smtp" && (
            <button disabled={busy} onClick={() => run(() => accountApi.clearMailSettings(), "Cleared.")}>
              Clear
            </button>
          )}
        </div>
      </>)}
      {cfg?.transport === "smtp" && (<>
        <label>Send a test message to<input value={testTo} placeholder="you@example.com" onChange={(e) => setTestTo(e.target.value)} /></label>
        <button disabled={busy || !testTo.trim()}
                onClick={() => run(() => accountApi.testMailSettings(testTo.trim()),
                  `Sent to ${testTo.trim()} — check the inbox.`)}>
          {busy ? "Sending…" : "Send test email"}
        </button>
      </>)}
      {note && <div className="muted small">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
