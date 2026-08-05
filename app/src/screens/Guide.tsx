import { useEffect, useState } from "react";
import { api, type DockFace, type DockFaces, type DockSettings,
         type HelpTopics, type Lesson, type Progress,
         type Walkthrough } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The guide — the walkthrough, what the help box can answer, and the pane the
 * helper lives in.
 *
 * This is the set of doorless routes it is least comfortable to have found.
 * The product has a **written walkthrough** that works with no model
 * configured, names the screens each step is about, and is held to the gallery
 * by a test — add a feature, draw its screen, and the suite fails until
 * somebody has written what it is for. All of that machinery, and no way for
 * anybody to take it.
 *
 * The console already had the help *box*: type a question, get an answer. What
 * was missing is the other half, and it is the half for the person who does not
 * yet know what to ask — which is most people, on their first minute.
 *
 * Two things the screen shows rather than styles away:
 *
 * - `guide`, the paragraph explaining why the guide has no name and no face.
 *   On a platform whose subject is synthetic people who look real, a guide with
 *   a persona would be the first thing you met that was not marked, and the
 *   product says so about itself;
 * - the dock's `refused` entry. `control` is not on the list of faces because
 *   assist, halt and approve are **actions**, and the dock does not act — it is
 *   a pane floating over the thing those buttons would stop. A catalogue that
 *   showed only what is available would hide the more interesting decision.
 */
export function Guide({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const learner = session.interactorId || me;

  const [walk, setWalk] = useState<Walkthrough | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [open, setOpen] = useState<Lesson | null>(null);
  const [topics, setTopics] = useState<HelpTopics | null>(null);

  const [faces, setFaces] = useState<DockFaces | null>(null);
  const [dock, setDock] = useState<DockSettings | null>(null);
  const [face, setFace] = useState<DockFace | null>(null);

  const [screen, setScreen] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.walkthrough().then(setWalk).catch(fail);
    api.helpTopics().then(setTopics).catch(() => undefined);
    api.dockFaces().then(setFaces).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!learner) return;
    api.progress(learner).then(setProgress).catch(() => setProgress(null));
  }, [learner]);

  useEffect(() => {
    if (!me || !token) return;
    api.dockSettings(me, token).then(setDock).catch(() => setDock(null));
  }, [me, token]);

  return (
    <div className="screen">
      <h2>{tr("gde.title", lang)}</h2>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {walk && (
        <div className="card">
          {/* The product explaining its own guide. Shown, not summarised. */}
          <p className="muted small">{walk.guide}</p>
        </div>
      )}

      {progress && (
        <div className="card">
          <h3>{tr("gde.whereyouare", lang)}</h3>
          <p className="small">
            {progress.note}
            {progress.finished && " " + tr("gde.beenthrough", lang)}
          </p>
          {progress.step && (
            <>
              <h4>{progress.step.title}</h4>
              <p className="small">{progress.step.what}</p>
              <p className="muted small">
                {fill(tr("gde.tryit", lang), { what: progress.step.try_it })}
                {progress.step.screens.length > 0 && (
                  <> · {fill(progress.step.screens.length === 1
                               ? tr("gde.screen.one", lang)
                               : tr("gde.screen.many", lang),
                             { list: progress.step.screens.join(", ") })}</>
                )}
              </p>
              <div className="row">
                <button disabled={!learner} onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    setProgress(await api.finishLesson(
                      learner, progress.step!.key));
                  } catch (e) { fail(e); }
                }}>{tr("gde.donenext", lang)}</button>
                <button disabled={!learner} onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    setProgress(await api.startWalkthrough(
                      learner, walk?.chapters[0]?.steps[0]?.key || "welcome"));
                    setNote(tr("gde.backtostart", lang));
                  } catch (e) { fail(e); }
                }}>{tr("gde.startagain", lang)}</button>
              </div>
            </>
          )}
        </div>
      )}

      <div className="card">
        <h3>{tr("gde.whatlooking", lang)}</h3>
        <p className="muted small">{tr("gde.everyscreen", lang)}</p>
        <div className="row">
          <input value={screen} onChange={(e) => setScreen(e.target.value)}
                 placeholder={tr("gde.screennum.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!screen.trim()} onClick={async () => {
            setError(null); setNote(null);
            try {
              setOpen(await api.lessonForScreen(Number(screen.trim())));
            } catch (e) { fail(e); setOpen(null); }
          }}>{tr("gde.lookitup", lang)}</button>
        </div>
        {open && (
          <>
            <h4>{open.title}</h4>
            <p className="muted small">{open.chapter}</p>
            <p className="small">{open.what}</p>
            <p className="muted small">
              {fill(tr("gde.tryit", lang), { what: open.try_it })}
            </p>
          </>
        )}
      </div>

      {walk && (
        <div className="card">
          <h3>{tr("gde.allofit", lang)}</h3>
          {walk.chapters.map((c) => (
            <div key={c.chapter}>
              <h4>{c.chapter}</h4>
              {c.steps.map((s) => (
                <div key={s.key} className="row">
                  <div style={{ flex: 1 }}>
                    <strong>{s.title}</strong>
                    <div className="muted small">
                      {s.screens.length > 0
                        ? fill(s.screens.length === 1
                                 ? tr("gde.screen.one", lang)
                                 : tr("gde.screen.many", lang),
                               { list: s.screens.join(", ") })
                        : tr("gde.noscreen", lang)}
                    </div>
                  </div>
                  <button onClick={async () => {
                    setError(null);
                    try { setOpen(await api.lesson(s.key)); }
                    catch (e) { fail(e); }
                  }}>{tr("gde.read", lang)}</button>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {topics && (
        <div className="card">
          <h3>{tr("gde.helpbox", lang)}</h3>
          <p className="muted small">{topics.disclosure}</p>
          <div className="row">
            {topics.topics.map((t) => (
              <span key={t} className="chip">{t.replace(/_/g, " ")}</span>
            ))}
          </div>
          <p className="muted small">{tr("gde.written", lang)}</p>
        </div>
      )}

      {faces && (
        <div className="card">
          <h3>{tr("gde.pane", lang)}</h3>
          {Object.entries(faces.faces).map(([name, shows]) => (
            <div key={name} className="row">
              <div style={{ flex: 1 }}>
                <strong>{name}</strong>
                <div className="muted small">{shows}</div>
              </div>
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  const r = await api.dockRoute(name);
                  setNote(tr("gde.routenote", lang)
                    .replace("{title}", r.title).replace("{path}", r.path)
                    .replace("{screen}", String(r.screen)));
                  if (me && token) setFace(await api.dockFace(me, name, token));
                } catch (e) { fail(e); }
              }}>{tr("gde.wheredoes", lang)}</button>
            </div>
          ))}

          {/* The more interesting half of the catalogue. */}
          {Object.entries(faces.refused).map(([name, why]) => (
            <p key={name} className="small">
              {fill(tr("gde.refused", lang),
                    { name: <strong>{name}</strong>, why })}
            </p>
          ))}

          {dock && (
            <>
              <h4>{tr("gde.yours", lang)}</h4>
              <p className="muted small">
                {fill(tr("gde.dockline", lang), {
                  corner: dock.corner, state: dock.state, face: dock.face,
                })}
                {!dock.set && " " + tr("gde.defaultnotchosen", lang)}
                {dock.tucked && dock.why && (
                  <> {fill(tr("gde.tucked", lang), { why: dock.why })}</>
                )}
              </p>
              <div className="row">
                {Object.keys(faces.corners).map((c) => (
                  <button key={c} className="chip" disabled={!token}
                          onClick={async () => {
                    setError(null); setNote(null);
                    try {
                      setDock(await api.setDock(me, { corner: c }, token));
                    } catch (e) { fail(e); }
                  }}>{dock.corner === c ? "✓ " : ""}{c}</button>
                ))}
              </div>
              <div className="row">
                {Object.keys(faces.states).map((s) => (
                  <button key={s} className="chip" disabled={!token}
                          onClick={async () => {
                    setError(null); setNote(null);
                    try {
                      setDock(await api.setDock(me, { state: s }, token));
                    } catch (e) { fail(e); }
                  }}>{dock.state === s ? "✓ " : ""}{s}</button>
                ))}
              </div>
            </>
          )}

          {face && (
            <>
              <h4>{face.face}</h4>
              <p className="small">{face.shows}</p>
              <p className="muted small">
                {face.acts
                  ? tr("gde.canact", lang)
                  : tr("gde.neveracts", lang)}{" "}
                {fill(tr("gde.nevercarries", lang),
                      { list: face.never.join(", ") })}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
