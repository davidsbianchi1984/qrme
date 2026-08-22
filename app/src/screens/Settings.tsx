import { useEffect, useState } from "react";
import { accountApi, api, getBase, getLlmKey, setBase, setLlmKey,
         type PairInfo } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
import { Problems } from "../Problems";
import { ProviderTiles } from "../ProviderTiles";
import { useSession } from "../store";

export function Settings({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session, signOut } = useSession();
  const lang = visitorLang();
  const [base, setBaseInput] = useState(getBase());
  const [llmKey, setLlmKeyInput] = useState(getLlmKey());
  const [keySaved, setKeySaved] = useState(false);
  const [offline, setOffline] = useState<Record<string, unknown> | null>(null);
  const [copiedExport, setCopiedExport] = useState(false);
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
        <h2>{tr("set.title", lang)}</h2>
        <span className="muted small">{tr("set.tag", lang)}</span>
      </header>

      <div className="card">
        <h3>{tr("set.api", lang)}</h3>
        <p className="muted small">{tr("set.api.lead", lang)}</p>
        <label>
          {tr("set.api.url", lang)}
          <input value={base} onChange={(e) => setBaseInput(e.target.value)} />
        </label>
        <button className="primary" onClick={save}>{saved ? tr("set.saved", lang) : tr("set.save", lang)}</button>
        <Refusal error={error} onPlans={onPlans} variant="inline" />
      </div>

      <ModelPanel onPlans={onPlans} />

      <MailPanel onPlans={onPlans} />

      <div className="card">
        <h3>{tr("set.key", lang)}</h3>
        <p className="muted small">{tr("set.key.lead", lang)}</p>
        <label>{tr("set.key.label", lang)}
          <input type="password" value={llmKey} placeholder={tr("set.key.ph", lang)}
                 onChange={(e) => setLlmKeyInput(e.target.value)} />
        </label>
        {/* Whose bill this is.
         *
         *     asked     can somebody use their own key
         *     mattered  do they know what changes when they do
         *
         * During the beta this deployment's own keys are what everybody
         * is spending, and they are being spent on purpose — an owner
         * paying so testers can try the thing without a card. The moment
         * somebody puts their own key in this box that stops being true
         * for them, and it stops silently. Said here, at the box, rather
         * than in terms nobody opens. */}
        <p className="muted small">{tr("set.key.whosebill", lang)}</p>
        <button className="primary" onClick={() => {
          setLlmKey(llmKey); setKeySaved(true); setTimeout(() => setKeySaved(false), 1500);
        }}>{keySaved ? tr("set.saved", lang)
            : llmKey.trim() ? tr("set.key.save", lang)
            : tr("set.key.clear", lang)}</button>
      </div>

      {/* Plain sentences instead of a JSON dump — a field report read the
          raw object and asked what the use was. What was useful in it stays;
          it is just said. And the thing they wanted the space for is here
          too: everything the profile is made of, copyable as one document,
          for feeding to whatever model or tool they choose — it is their
          material.

          The "Who wrote this?" card that used to sit below this one is gone,
          not moved: the accountless screen has the same verifier, and the
          same control twice teaches people that neither is the real one. */}
      <div className="card">
        <h3>{tr("set.offline", lang)}</h3>
        {offline ? (
          <>
            <p className="small">
              {offline.offline
                ? tr("set.offline.on", lang)
                : tr("set.offline.off", lang)}
            </p>
            {typeof offline.provider === "string" && (
              <p className="muted small">{offline.provider}</p>
            )}
            {typeof offline.data_locality === "string" && (
              <p className="muted small">{offline.data_locality}</p>
            )}
            {Array.isArray(offline.guarantees)
              && offline.guarantees.map((g, i) => (
                <p className="muted small" key={i}>· {String(g)}</p>
              ))}
          </>
        ) : (
          <div className="muted">{tr("set.offline.unreachable", lang)}</div>
        )}
        {session.profileId && session.ownerToken && (
          <>
            <h4>{tr("set.export", lang)}</h4>
            <p className="muted small">{tr("set.export.pitch", lang)}</p>
            <button onClick={async () => {
              try {
                const bundle = await api.exportProfile(
                  session.profileId!, session.ownerToken!);
                await navigator.clipboard.writeText(
                  JSON.stringify(bundle, null, 2));
                setCopiedExport(true);
                setTimeout(() => setCopiedExport(false), 2000);
              } catch (e) { setError(e); }
            }}>
              {copiedExport ? "✓" : tr("set.export.copy", lang)}
            </button>
          </>
        )}
      </div>

      {pair && (
        <div className="card">
          <h3>{tr("set.pair", lang)}</h3>
          <p className="muted small">{pair.note}</p>
          <div className="pair">
            {/* The literal rather than `pair.qr_svg`, which says the same
                thing: a path built from a response field is invisible to the
                route audit, and this door counted as missing for as long as
                it was written that way. */}
            <img className="pair-qr" src={getBase() + "/pair/qr.svg"} alt={tr("set.pair.alt", lang)} />
            <div>
              <div className="mono pair-url">{pair.console_url}</div>
              <ol className="pair-steps">{pair.how.map((s) => <li key={s}>{s}</li>)}</ol>
            </div>
          </div>
        </div>
      )}
      <div className="card">
        <h3>{tr("set.session", lang)}</h3>
        <div className="muted small">
          {fill(tr("set.session.profile", lang),
                { id: session.profileId })}
        </div>
        <button className="danger" onClick={signOut}>{tr("set.session.out", lang)}</button>
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
  const lang = visitorLang();
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
      <h3>{tr("set.mail", lang)}</h3>
      <p className="muted small">
        {cfg?.transport === "smtp"
          ? fill(tr("set.mail.smtp", lang),
                 { host: <b>{cfg.host}</b>,
                   env: cfg.source === "environment"
                     ? " (set by environment variables)" : "" })
          : tr("set.mail.none", lang)}
      </p>
      {cfg?.source !== "environment" && (<>
        <div className="row">
          <label>{tr("set.mail.host", lang)}<input value={host} placeholder={tr("set.mail.host.ph", lang)} onChange={(e) => setHost(e.target.value)} /></label>
          <label>{tr("set.mail.port", lang)}<input type="number" value={port} onChange={(e) => setPort(Number(e.target.value))} /></label>
        </div>
        <label>{tr("set.mail.user", lang)}<input value={username} placeholder={tr("set.mail.user.ph", lang)} onChange={(e) => setUsername(e.target.value)} /></label>
        <label>{tr("set.mail.pass", lang)} {cfg?.password_set && <span className="muted small">{tr("set.mail.pass.saved", lang)}</span>}
          <input type="password" value={password} placeholder={tr("set.mail.pass.ph", lang)} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <label>{tr("set.mail.from", lang)}<input value={sender} placeholder={tr("set.mail.user.ph", lang)} onChange={(e) => setSender(e.target.value)} /></label>
        <label>{tr("set.mail.link", lang)} <span className="muted small">{tr("set.mail.link.note", lang)}</span>
          <input value={publicUrl} placeholder={tr("set.mail.link.ph", lang)} onChange={(e) => setPublicUrl(e.target.value)} />
        </label>
        <div className="actions">
          <button className="primary" disabled={busy || !host.trim()}
                  onClick={() => run(() => accountApi.saveMailSettings({
                    host, port, username, password: password || undefined,
                    sender, public_url: publicUrl }),
                    tr("set.mail.saved.note", lang))}>
            {busy ? tr("set.saving", lang) : tr("set.mail.save", lang)}
          </button>
          {cfg?.transport === "smtp" && (
            <button disabled={busy} onClick={() => run(() => accountApi.clearMailSettings(),
                                     tr("set.mail.cleared.note", lang))}>
              {tr("set.mail.clear", lang)}
            </button>
          )}
        </div>
      </>)}
      {cfg?.transport === "smtp" && (<>
        <label>{tr("set.mail.test", lang)}<input value={testTo} placeholder={tr("set.mail.test.ph", lang)} onChange={(e) => setTestTo(e.target.value)} /></label>
        <button disabled={busy || !testTo.trim()}
                onClick={() => run(() => accountApi.testMailSettings(testTo.trim()),
                  tr("set.mail.sent.note", lang)
                    .replace("{to}", testTo.trim()))}>
          {busy ? tr("set.mail.sending", lang) : tr("set.mail.test.send", lang)}
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
  const lang = visitorLang();
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
      <h3>{tr("set.model", lang)}</h3>
      <p className="muted small">{tr("set.model.lead", lang)}</p>
      <ProviderTiles providers={providers} chosen={chosen}
                     effective={effective} onPick={pick} busy={busy} />
      {/* The truth about what will actually answer. The silent case was the
          bad one: Automatic quietly resolving to the stub while the screen
          full of logos implied a real model was on. */}
      {effective === "stub" && chosen !== "stub" ? (
        <div className="degraded">
          {tr("set.model.stub", lang)}
        </div>
      ) : effective && chosen !== "auto" && chosen !== effective && (
        <div className="degraded">
          {fill(tr("set.model.resolves", lang),
                { effective: <b>{effective}</b> })}
        </div>
      )}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
