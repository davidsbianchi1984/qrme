import { useEffect, useMemo, useState } from "react";
import { api, type AppConnector, type ConnectorCatalogue } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The plug-in storefront — the whole board, and what each row can reach.
 *
 * The connector catalogue has existed since the connected-apps round and the
 * only way to see it was the picker inside another screen: a `<select>` of
 * providers, chosen before you knew what any of them were. A person who
 * wants their inbox read does not go looking for a dropdown labelled
 * *provider*; they look for a shop.
 *
 *     asked     can a profile connect to an outside service
 *     mattered  can a person find out which ones, and what happens then
 *
 * ## The lock is a posture, not a picture
 *
 * Every row carries `needs` from `qrme/catalog.py` — `nothing`, `sign-in` or
 * `key` — and the row draws a plus or a lock from it. The lock is not
 * decoration: an installed connector that has not been given its credential
 * is refused by `invoke` with a sentence naming what is missing. Before this
 * round that call answered *performed* for every row on the board, having
 * reached nothing at all.
 *
 * The credential goes to the vault and never to this console's own store —
 * the field here writes it once, to `POST /apps/{cid}/authorize`, and there
 * is nothing that reads it back.
 *
 * ## Uninstall
 *
 * `DELETE /apps/{cid}` has existed as long as connectors have, and no client
 * of the four ever called it. The door guard could not see it: its skip list
 * held `/app` for the console bundle, and `/apps` starts with `/app`. So
 * somebody could connect their inbox to a profile and had no way at all to
 * disconnect it. This screen is where that button finally is.
 *
 * ## Why the rows say what they say
 *
 * The one-line description under each name is the row's own capabilities,
 * three of them, joined. Not blurb — a hundred and three hand-written
 * sentences would be a hundred and three things to drift out of agreement
 * with what the connector actually offers, and the capability list is the
 * thing the backend checks a call against.
 */

/** A glyph per family. The families come from the backend; this is only how
 *  they look, so a family added there shows up here with a plug and a name
 *  rather than not showing up at all. */
const ICONS: Record<string, string> = {
  apple: "", google: "🌈", microsoft: "🪟", canva: "🎨",
  glasses: "👓", gaming: "🎮", work: "💼", search: "🔎", scrape: "🌐",
};

/** The lock, and what it is about. `nothing` gets no lock at all. */
const LOCK: Record<string, string> = {
  "sign-in": "🔒", key: "🔑",
};

export function Plugins({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const L = (key: string) => tr(key, lang);

  const [board, setBoard] = useState<ConnectorCatalogue | null>(null);
  const [mine, setMine] = useState<AppConnector[]>([]);
  const [find, setFind] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);
  // Which installed connector is having its credential typed, and what into.
  const [signing, setSigning] = useState<string | null>(null);
  const [secret, setSecret] = useState("");
  const [account, setAccount] = useState("");
  // Using one. The console could list and connect connectors and never use
  // one — collecting and invoking were phone-only, and nothing said so.
  const [using, setUsing] = useState<AppConnector | null>(null);
  const [words, setWords] = useState("");
  const [pick, setPick] = useState("");
  const [said, setSaid] = useState<string | null>(null);

  useEffect(() => {
    api.connectorCatalogue().then(setBoard).catch(() => setBoard(null));
  }, []);

  useEffect(() => {
    if (!session.profileId || !session.ownerToken) return;
    api.profileApps(session.profileId, session.ownerToken)
      .then(setMine).catch(() => setMine([]));
  }, [session.profileId, session.ownerToken]);

  async function reload() {
    if (!session.profileId || !session.ownerToken) return;
    setMine(await api.profileApps(session.profileId, session.ownerToken));
  }

  async function add(provider: string, app: string) {
    if (!session.profileId || !session.ownerToken) return;
    setBusy(`${provider}/${app}`); setError(null);
    try {
      await api.connectApp(session.profileId, { provider, app },
                           session.ownerToken);
      await reload();
    } catch (e) { setError(e); }
    finally { setBusy(null); }
  }

  async function remove(cid: string) {
    if (!session.ownerToken) return;
    setBusy(cid); setError(null);
    try {
      await api.revokeApp(cid, session.ownerToken);
      await reload();
    } catch (e) { setError(e); }
    finally { setBusy(null); }
  }

  async function signIn(cid: string) {
    if (!session.ownerToken || !secret.trim()) return;
    setBusy(cid); setError(null);
    try {
      await api.authorizeApp(
        cid, { secret: secret.trim(), account: account.trim() || undefined },
        session.ownerToken);
      setSigning(null); setSecret(""); setAccount("");
      await reload();
    } catch (e) { setError(e); }
    finally { setBusy(null); }
  }

  /** Pull what the owner pasted into the profile's source material. This is
   *  the honest shape of `collect` and always has been: it stores what it is
   *  given rather than fetching, which is why it needs no credential. */
  async function pullIn(c: AppConnector) {
    if (!session.ownerToken || !words.trim()) return;
    setBusy(c.id); setError(null); setSaid(null);
    try {
      const done = await api.collectFromApp(
        c.id, { items: [{ content: words.trim(), title: c.label }] },
        session.ownerToken);
      setSaid(done.note); setWords("");
      await reload();
    } catch (e) { setError(e); }
    finally { setBusy(null); }
  }

  /** Use one of the capabilities the connector was granted. Refused, loudly,
   *  when the connector has no credential — that refusal is the lock. */
  async function use(c: AppConnector) {
    if (!session.ownerToken || !pick) return;
    setBusy(c.id); setError(null); setSaid(null);
    try {
      const done = await api.invokeApp(
        c.id, { capability: pick, input: words.trim() || undefined },
        session.ownerToken);
      setSaid(done.result); setWords("");
      await reload();
    } catch (e) { setError(e); }
    finally { setBusy(null); }
  }

  /** What is installed, by catalogue key, so a row knows its own state. */
  const installed = useMemo(() => {
    const out: Record<string, AppConnector> = {};
    for (const c of mine) if (c.status === "active") out[`${c.provider}/${c.app}`] = c;
    return out;
  }, [mine]);

  const needle = find.trim().toLowerCase();

  function matches(label: string, app: string, caps: string[]): boolean {
    if (!needle) return true;
    return [label, app, ...caps].some(
      (s) => s.toLowerCase().includes(needle));
  }

  function row(provider: string, app: string, label: string,
               caps: string[], needs: string) {
    const key = `${provider}/${app}`;
    const have = installed[key];
    const working = busy === key || (have && busy === have.id);
    return (
      <li key={key} className="plug-row">
        <span className="plug-icon" aria-hidden="true">
          {ICONS[provider] ?? "🔌"}
        </span>
        <span className="plug-what">
          <strong>{label}</strong>
          <span className="muted small">{caps.slice(0, 3).join(" · ")}</span>
        </span>
        {needs !== "nothing" && (
          <span className="plug-lock" title={L(`plugins.needs.${needs}`)}>
            {LOCK[needs]}
          </span>
        )}
        {have ? (
          <>
            {needs !== "nothing" && !have.authorized && (
              <button disabled={working}
                      onClick={() => { setSigning(have.id); setSecret(""); }}>
                {L("plugins.signin")}
              </button>
            )}
            {have.authorized && (
              <span className="plug-on small">{L("plugins.on")}</span>
            )}
            <button disabled={working} onClick={() => remove(have.id)}>
              {L("plugins.remove")}
            </button>
          </>
        ) : (
          <button className="primary" disabled={working || !session.ownerToken}
                  onClick={() => add(provider, app)}>
            {L("plugins.add")}
          </button>
        )}
      </li>
    );
  }

  if (!session.profileId) {
    return (
      <div className="screen">
        <header className="screen-head"><h2>{L("nav.plugins")}</h2></header>
        <div className="card"><p className="muted center">
          {L("plugins.signedout")}
        </p></div>
      </div>
    );
  }

  const ready = (board?.providers ?? []).flatMap((p) =>
    p.apps.filter((a) => a.needs === "nothing")
      .map((a) => ({ provider: p.provider, ...a })));

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{L("nav.plugins")}</h2>
        <p className="muted small">{L("plugins.pitch")}</p>
      </header>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      <div className="card">
        <input className="plug-find" value={find}
               placeholder={L("plugins.search")}
               onChange={(e) => setFind(e.target.value)} />
        {board && (
          <p className="muted small">
            {fill(L("plugins.count"), {
              apps: String(board.app_count),
              families: String(board.provider_count),
            })}
          </p>
        )}
      </div>

      {/* What is on already. First, because it is the thing somebody came
          back to change — and because it is the only place uninstall is. */}
      <div className="card">
        <strong>{L("plugins.installed")}</strong>
        {mine.filter((c) => c.status === "active").length === 0 ? (
          <p className="muted small">{L("plugins.none")}</p>
        ) : (
          <ul className="plug-list">
            {mine.filter((c) => c.status === "active").map((c) => (
              <li key={c.id} className="plug-row">
                <span className="plug-icon" aria-hidden="true">
                  {ICONS[c.provider] ?? "🔌"}
                </span>
                <span className="plug-what">
                  <strong>{c.label}</strong>
                  <span className="muted small">
                    {c.authorized ? L("plugins.on")
                                  : L(`plugins.needs.${c.needs}`)}
                  </span>
                </span>
                {!c.authorized && c.needs !== "nothing" && (
                  <button disabled={busy === c.id}
                          onClick={() => { setSigning(c.id); setSecret(""); }}>
                    {L("plugins.signin")}
                  </button>
                )}
                <button disabled={busy === c.id}
                        onClick={() => {
                          setUsing(c); setSaid(null); setWords("");
                          setPick(c.capabilities[0] ?? "");
                        }}>
                  {L("plugins.use")}
                </button>
                <button disabled={busy === c.id} onClick={() => remove(c.id)}>
                  {L("plugins.remove")}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* The credential, typed once and gone. It is written to the vault by
          the route; nothing on this screen reads it back, and closing the
          box is the whole of forgetting it. */}
      {signing && (
        <div className="card">
          <strong>{L("plugins.signin")}</strong>
          <p className="muted small">{L("plugins.signin.sub")}</p>
          <input type="password" value={secret}
                 placeholder={L("plugins.secret")}
                 onChange={(e) => setSecret(e.target.value)} />
          <input value={account} placeholder={L("plugins.account")}
                 onChange={(e) => setAccount(e.target.value)} />
          <div className="row">
            <button className="primary" disabled={busy === signing || !secret.trim()}
                    onClick={() => signIn(signing)}>
              {L("plugins.signin.go")}
            </button>
            <button onClick={() => { setSigning(null); setSecret(""); }}>
              {L("agent.asks.no")}
            </button>
          </div>
        </div>
      )}

      {/* Using one. Two halves, because the connector's `directions` say
          which it has: `collect` takes what you paste and makes it source
          material; `act` and `produce` drive the service, and are where the
          lock is felt — an unsigned-in connector refuses here by name. */}
      {using && (
        <div className="card">
          <div className="row">
            <strong style={{ flex: 1 }}>{using.label}</strong>
            <button onClick={() => { setUsing(null); setSaid(null); }}>
              {L("studio.reach.hide")}
            </button>
          </div>
          {said && <p className="muted small">{said}</p>}
          <textarea rows={3} value={words}
                    placeholder={L("plugins.words")}
                    onChange={(e) => setWords(e.target.value)} />
          <div className="row">
            {using.directions.includes("collect") && (
              <button disabled={busy === using.id || !words.trim()}
                      onClick={() => pullIn(using)}>
                {L("plugins.pull")}
              </button>
            )}
            {(using.directions.includes("act")
              || using.directions.includes("produce")) && (
              <>
                <select value={pick} onChange={(e) => setPick(e.target.value)}>
                  {using.capabilities.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                <button className="primary"
                        disabled={busy === using.id || !pick}
                        onClick={() => use(using)}>
                  {L("plugins.do")}
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Works the moment it is added. Named for what is true of these rows
          rather than "Featured", which would be an editorial claim nothing
          in this repository is in a position to make. */}
      {ready.length > 0 && (
        <div className="card">
          <strong>{L("plugins.ready")}</strong>
          <p className="muted small">{L("plugins.ready.sub")}</p>
          <ul className="plug-list">
            {ready.filter((a) => matches(a.label, a.app, a.capabilities))
              .map((a) => row(a.provider, a.app, a.label,
                              a.capabilities, a.needs))}
          </ul>
        </div>
      )}

      {(board?.providers ?? []).map((p) => {
        const rows = p.apps.filter(
          (a) => matches(a.label, a.app, a.capabilities));
        if (rows.length === 0) return null;
        return (
          <div className="card" key={p.provider}>
            <strong>
              <span aria-hidden="true">{ICONS[p.provider] ?? "🔌"}</span> {p.label}
            </strong>
            <ul className="plug-list">
              {rows.map((a) => row(p.provider, a.app, a.label,
                                   a.capabilities, a.needs))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}
