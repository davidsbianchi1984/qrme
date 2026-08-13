/**
 * The Studio — where somebody writes their own tools for their own profile.
 *
 * A widget is a function they wrote. It runs in a box with no network, one
 * directory, no child processes and finite time; `qrme/widgets.py` holds
 * those walls and `tests/test_the_widget_cannot_leave_its_box.py` proves
 * they hold. Nothing on this screen can reach another profile, because
 * every door it knocks on is owner-scoped at the API and scoped again in
 * the query behind it.
 *
 * The limits are fetched rather than written here. A screen that states a
 * number the runner does not hold is a promise the product did not make,
 * and this one has five of them to get wrong.
 */
import { useCallback, useEffect, useState } from "react";

import { api, type Widget, type WidgetRun } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

const STARTER = `// Your own tool. Whatever it returns is the answer.
module.exports = ({ name }) => {
  return "hello, " + (name || "you");
};
`;

export function Studio({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [box, setBox] = useState<{ available: boolean;
                                   unavailable_because: string | null;
                                   allowances: Record<string, number> } | null>(null);
  const [open, setOpen] = useState<Widget | null>(null);
  const [name, setName] = useState("");
  const [source, setSource] = useState(STARTER);
  const [answer, setAnswer] = useState<WidgetRun | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  const owner = session.profileId && session.ownerToken;

  const load = useCallback(() => {
    if (!owner) return;
    api.listWidgets(session.profileId!, session.ownerToken!)
      .then((r) => setWidgets(r.widgets))
      .catch((e) => setError(e));
  }, [owner, session.profileId, session.ownerToken]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { api.studioLimits().then(setBox).catch(() => {}); }, []);

  function edit(widget: Widget | null) {
    setOpen(widget);
    setName(widget ? widget.name : "");
    setSource(widget ? widget.source : STARTER);
    setAnswer(null);
    // Re-read the one being opened rather than trusting the list. A list
    // fetched a minute ago is a draft from a minute ago, and the editor is
    // where somebody's own words go — opening a stale copy and saving it is
    // how an edit made on another device disappears.
    if (widget && owner) {
      api.readWidget(session.profileId!, widget.id, session.ownerToken!)
        .then((fresh) => {
          setOpen(fresh);
          setName(fresh.name);
          setSource(fresh.source);
        })
        .catch((e) => setError(e));
    }
  }

  function save() {
    if (!owner) return;
    setBusy(true);
    const body = { name, source };
    const call = open
      ? api.updateWidget(session.profileId!, open.id, body, session.ownerToken!)
      : api.createWidget(session.profileId!, body, session.ownerToken!);
    call.then((w) => { setOpen(w); load(); })
      .catch((e) => setError(e))
      .finally(() => setBusy(false));
  }

  function run() {
    if (!owner || !open) return;
    setBusy(true);
    setAnswer(null);
    api.runWidget(session.profileId!, open.id, undefined, session.ownerToken!)
      .then(setAnswer)
      .catch((e) => setError(e))
      .finally(() => setBusy(false));
  }

  function remove(widget: Widget) {
    if (!owner) return;
    api.deleteWidget(session.profileId!, widget.id, session.ownerToken!)
      .then(() => { if (open?.id === widget.id) edit(null); load(); })
      .catch((e) => setError(e));
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("studio.title", lang)}</h2>
        <span className="muted small">{tr("studio.sub", lang)}</span>
      </header>

      {error != null && <Refusal error={error} onPlans={onPlans} />}

      {!owner && (
        <div className="card"><p className="muted small">
          {tr("studio.owneronly", lang)}
        </p></div>
      )}

      {/* The honest state on a host that cannot build the box. The editor
          still opens — somebody may want to write and keep a widget for a
          deployment that can run it — and the run button says why not. */}
      {box && !box.available && (
        <div className="card"><p className="muted small">
          {tr("studio.noBox", lang)}
        </p></div>
      )}

      <div className="card">
        <div className="row">
          <strong style={{ flex: 1 }}>{tr("studio.yours", lang)}</strong>
          <button className="primary" onClick={() => edit(null)}>
            {tr("studio.new", lang)}
          </button>
        </div>
        {widgets.length === 0 && (
          <p className="muted small">{tr("studio.none", lang)}</p>
        )}
        {widgets.map((w) => (
          <div key={w.id} className="row">
            <button style={{ flex: 1, textAlign: "left" }}
                    onClick={() => edit(w)}>
              {w.name}
            </button>
            <span className="muted small">
              {fill(tr("studio.version", lang), { n: String(w.version) })}
            </span>
            <button onClick={() => remove(w)}>{tr("studio.remove", lang)}</button>
          </div>
        ))}
      </div>

      <div className="card">
        <label>
          <span className="muted small">{tr("studio.name", lang)}</span>
          <input value={name} onChange={(e) => setName(e.target.value)}
                 placeholder={tr("studio.name.ph", lang)} />
        </label>
        <label>
          <span className="muted small">{tr("studio.source", lang)}</span>
          <textarea className="code" rows={14} value={source} spellCheck={false}
                    onChange={(e) => setSource(e.target.value)} />
        </label>
        <div className="row">
          <button className="primary" disabled={busy || !owner || !name.trim()}
                  onClick={save}>
            {busy ? tr("studio.saving", lang) : tr("studio.save", lang)}
          </button>
          <button disabled={busy || !open || !(box?.available ?? true)}
                  onClick={run}>
            {tr("studio.run", lang)}
          </button>
        </div>
        {/* Read from the runner rather than restated here. */}
        {box && (
          <p className="muted small">
            {fill(tr("studio.limits.line", lang), {
              seconds: String(box.allowances.wall_seconds),
              memory: String(box.allowances.heap_mb),
              size: String(Math.round(box.allowances.source_bytes / 1024)),
            })}
          </p>
        )}
        <p className="muted small">{tr("studio.walls", lang)}</p>
      </div>

      {answer && (
        <div className="card">
          <div className="row">
            <strong style={{ flex: 1 }}>
              {tr(`studio.status.${answer.status}`, lang)}
            </strong>
            <span className="muted small">
              {fill(tr("studio.took", lang), { ms: String(answer.ms) })}
            </span>
          </div>
          {answer.said && <p className="muted small">{answer.said}</p>}
          {answer.message && <pre className="code">{answer.message}</pre>}
          {answer.status === "ok" && (
            answer.truncated
              ? <p className="muted small">{tr("studio.truncated", lang)}</p>
              : <pre className="code">{JSON.stringify(answer.value, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );
}
