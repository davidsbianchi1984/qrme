import { useEffect, useState } from "react";
import { accountApi, api, getBase, getLlmKey, setBase, setLlmKey, type PairInfo,
         type WatermarkRecovery } from "../api";
import { Refusal } from "../Refusal";
import { t as tr, visitorLang } from "../l10n";
import { Problems } from "../Problems";
import { ProviderTiles } from "../ProviderTiles";
import { useSession } from "../store";

export function Settings({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session, signOut } = useSession();
  const [base, setBaseInput] = useState(getBase());
  const [llmKey, setLlmKeyInput] = useState(getLlmKey());
  const [keySaved, setKeySaved] = useState(false);
  const [offline, setOffline] = useState<Record<string, unknown> | null>(null);
  // "Who wrote this?" — the recoverable half of the watermark.
  const [checkText, setCheckText] = useState("");
  const [checked, setChecked] = useState<WatermarkRecovery | null>(null);
  const [checking, setChecking] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [pair, setPair] = useState<PairInfo | null>(null);

  useEffect(() => {
    api.offlineStatus().then(setOffline).catch(() => setOffline(null));
    api.pair().then(setPair).catch(() => setPair(null));
  }, []);

  function save() {
    setBase(base);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
    api.offlineStatus().then(setOffline).catch((e) => setError(e));
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Control Center</h2>
        <span className="muted small">you are in control</span>
      </header>

      <div className="card">
        <h3>API connection — where this app's own server lives</h3>
        <p className="muted small">
          This is the <b>address of the QRME backend</b> this console talks
          to (the desktop app starts its own; a phone points here over
          Wi-Fi). It is an address, not a secret — and it is <b>not</b> the
          model API key below: the two are different things.
        </p>
        <label>
          Backend base URL
          <input value={base} onChange={(e) => setBaseInput(e.target.value)} />
        </label>
        <button className="primary" onClick={save}>{saved ? "Saved ✓" : "Save"}</button>
        <Refusal error={error} onPlans={onPlans} variant="inline" />
      </div>

      <ModelPanel onPlans={onPlans} />

      <MailPanel onPlans={onPlans} />

      <div className="card">
        <h3>Your model API key — who pays for the AI's words</h3>
        <p className="muted small">
          Different from the connection above: that was <b>where</b> this app's
          server lives; this is <b>whose credential the AI generation runs
          on</b>. Paste your own key (Anthropic <code>sk-ant-…</code>, or
          OpenAI / xAI / Gemini for those providers) and your profiles'
          replies run on your credential. It is a secret: it stays on this
          device and rides only your own requests — the server never stores
          it. Leave it empty to use whatever key the deployment lends.
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

      {/* The recoverable watermark: paste text, learn whether one of this
          deployment's profiles wrote it — and it survives editing. */}
      <div className="card">
        <h3>Who wrote this? — check any text</h3>
        <p className="muted small">
          Paste writing you think came from a profile here. It answers from the
          text alone, with no credential id, and still answers when the text
          has been edited.
        </p>
        <textarea rows={4} value={checkText} placeholder="Paste the text…"
                  onChange={(e) => setCheckText(e.target.value)} />
        <button disabled={checking || !checkText.trim()}
                onClick={async () => {
                  setChecking(true);
                  try { setChecked(await api.recoverWatermark(checkText)); }
                  catch { setChecked(null); }
                  finally { setChecking(false); }
                }}>{checking ? "Checking…" : "Check it"}</button>
        {checked && (checked.recovered ? (
          <div className="guidance">
            <div className="guidance-src">
              {checked.display?.mark} produced by {checked.profile_id} · {checked.state}
            </div>
            <p>
              {checked.matched_windows} of {checked.stored_windows} passages
              match ({Math.round((checked.similarity || 0) * 100)}% similar).
              {checked.verbatim
                ? " The text is exactly what was stamped."
                : " The text has been altered since it was written."}
            </p>
            <div className="muted small">{checked.method}</div>
          </div>
        ) : (
          <div className="guidance">
            <p>No profile here wrote this.</p>
            <div className="muted small">{checked.reason}</div>
          </div>
        ))}
      </div>

      {pair && (
        <div className="card">
          <h3>Open on your phone</h3>
          <p className="muted small">{pair.note}</p>
          <div className="pair">
            {/* The literal rather than `pair.qr_svg`, which says the same
                thing: a path built from a response field is invisible to the
                route audit, and this door counted as missing for as long as
                it was written that way. */}
            <img className="pair-qr" src={getBase() + "/pair/qr.svg"} alt="QR code for the studio URL on this network" />
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
      <Problems />
    </div>
  );
}


// Where this deployment sends mail through. Until a host is set here (or in
// the environment), no verification email can reach anybody — the message
// goes to the server's log instead, which is why local signup does not wait
// for one. Fill this in and the emails become real.
function MailPanel({ onPlans }: { onPlans: () => void }) {
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
  const [error, setError] = useState<unknown>(null);

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
    catch (e) { setError(e); }
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
      <FeatureSwitches />
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}

// The person's switches. Everything downstream refuses by naming the
// switch, which is what makes a toggle worth having.
function FeatureSwitches() {
  const { session } = useSession();
  const lang = visitorLang();
  const [flags, setFlags] = useState<Record<string, boolean> | null>(null);
  const [note, setNote] = useState<string | null>(null);

  useEffect(() => {
    if (!session.profileId || !session.ownerToken) return;
    api.getFeatures(session.profileId, session.ownerToken)
      .then(setFlags).catch(() => setFlags(null));
  }, [session.profileId, session.ownerToken]);

  if (!flags) return null;

  async function flip(feature: string, enabled: boolean) {
    if (!session.profileId || !session.ownerToken) return;
    try {
      setFlags(await api.setFeature(session.profileId, feature, enabled,
                                    session.ownerToken));
      setNote(null);
    } catch (e) { setNote((e as Error).message); }
  }

  return (
    <div className="card">
      <h3>{tr("switches.title", lang)}</h3>
      <p className="muted small">{tr("switches.note", lang)}</p>
      {Object.entries(flags).map(([feature, on]) => (
        <label key={feature} className="row">
          <input type="checkbox" checked={on}
                 onChange={(e) => flip(feature, e.target.checked)} />
          <span>{tr(`switches.${feature}`, lang)}</span>
        </label>
      ))}
      {note && <div className="muted small">{note}</div>}
    </div>
  );
}


// Which model answers for this profile — click a tile. The switchboard has
// always been in the backend; a person should not have to know a PUT exists.
function ModelPanel({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const [providers, setProviders] = useState<Awaited<ReturnType<typeof accountApi.listModels>>["providers"]>([]);
  const [chosen, setChosen] = useState("auto");
  const [effective, setEffective] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  function load() {
    accountApi.listModels().then((m) => setProviders(m.providers)).catch(() => setProviders([]));
    if (session.profileId) {
      accountApi.getProfileModel(session.profileId)
        .then((c) => { setChosen(c.provider); setEffective(c.effective); })
        .catch(() => undefined);
    }
  }
  useEffect(load, [session.profileId]);

  async function pick(name: string) {
    if (!session.profileId || !session.ownerToken) return;
    setBusy(true); setError(null);
    try {
      const r = await accountApi.setProfileModel(session.profileId, name, session.ownerToken);
      setChosen(r.provider); setEffective(r.effective);
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>Which model answers</h3>
      <p className="muted small">
        Your profile's replies can run on any of these. Pick one and every
        reply uses it; <b>Automatic</b> uses whichever is configured.
      </p>
      <ProviderTiles providers={providers} chosen={chosen}
                     effective={effective} onPick={pick} busy={busy} />
      {/* The truth about what will actually answer. The silent case was the
          bad one: Automatic quietly resolving to the stub while the screen
          full of logos implied a real model was on. */}
      {effective === "stub" && chosen !== "stub" ? (
        <div className="degraded">
          ⚠ Right now replies come from the <b>built-in offline helper</b> —
          no online model has a working key on this deployment. Pick a
          provider above and add its key.
        </div>
      ) : effective && chosen !== "auto" && chosen !== effective && (
        <div className="degraded">
          ⚠ Right now it resolves to <b>{effective}</b> — the one you picked
          has no key on this deployment yet.
        </div>
      )}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
