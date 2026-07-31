import { useEffect, useState } from "react";
import { api, type DockFace, type DockFaces, type DockSettings,
         type HelpTopics, type Lesson, type Progress,
         type Walkthrough } from "../api";
import { useSession } from "../store";

/**
 * The guide — the walkthrough, what the help box can answer, and the pane the
 * helper lives in.
 *
 * This is the set of doorless routes it is least comfortable to have found.
 * The product has a **thirty-eight-lesson written walkthrough** that works with
 * no model configured, names the screens each step is about, and is held to the
 * gallery by a test — add a feature, draw its screen, and the suite fails until
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
export function Guide() {
  const { session } = useSession();
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
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const fail = (e: unknown) => setError((e as Error).message);

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
      <h2>Show me around</h2>

      {error && <div className="card error">{error}</div>}
      {note && <div className="card"><p className="small">{note}</p></div>}

      {walk && (
        <div className="card">
          {/* The product explaining its own guide. Shown, not summarised. */}
          <p className="muted small">{walk.guide}</p>
        </div>
      )}

      {progress && (
        <div className="card">
          <h3>Where you are</h3>
          <p className="small">
            {progress.note}
            {progress.finished && " — you have been through all of it."}
          </p>
          {progress.step && (
            <>
              <h4>{progress.step.title}</h4>
              <p className="small">{progress.step.what}</p>
              <p className="muted small">
                Try it: {progress.step.try_it}
                {progress.step.screens.length > 0 && (
                  <> · screen{progress.step.screens.length === 1 ? "" : "s"}{" "}
                    {progress.step.screens.join(", ")}</>
                )}
              </p>
              <div className="row">
                <button disabled={!learner} onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    setProgress(await api.finishLesson(
                      learner, progress.step!.key));
                  } catch (e) { fail(e); }
                }}>Done — next</button>
                <button disabled={!learner} onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    setProgress(await api.startWalkthrough(
                      learner, walk?.chapters[0]?.steps[0]?.key || "welcome"));
                    setNote("Back to the beginning.");
                  } catch (e) { fail(e); }
                }}>Start again</button>
              </div>
            </>
          )}
        </div>
      )}

      <div className="card">
        <h3>What am I looking at?</h3>
        <p className="muted small">
          Every screen in the gallery is explained by one of the lessons, and a
          test keeps that true — so a drawing can always be looked up.
        </p>
        <div className="row">
          <input value={screen} onChange={(e) => setScreen(e.target.value)}
                 placeholder="a screen number" style={{ flex: 1 }} />
          <button disabled={!screen.trim()} onClick={async () => {
            setError(null); setNote(null);
            try {
              setOpen(await api.lessonForScreen(Number(screen.trim())));
            } catch (e) { fail(e); setOpen(null); }
          }}>Look it up</button>
        </div>
        {open && (
          <>
            <h4>{open.title}</h4>
            <p className="muted small">{open.chapter}</p>
            <p className="small">{open.what}</p>
            <p className="muted small">Try it: {open.try_it}</p>
          </>
        )}
      </div>

      {walk && (
        <div className="card">
          <h3>All of it</h3>
          {walk.chapters.map((c) => (
            <div key={c.chapter}>
              <h4>{c.chapter}</h4>
              {c.steps.map((s) => (
                <div key={s.key} className="row">
                  <div style={{ flex: 1 }}>
                    <strong>{s.title}</strong>
                    <div className="muted small">
                      {s.screens.length > 0
                        ? <>screen{s.screens.length === 1 ? "" : "s"}{" "}
                            {s.screens.join(", ")}</>
                        : "no screen"}
                    </div>
                  </div>
                  <button onClick={async () => {
                    setError(null);
                    try { setOpen(await api.lesson(s.key)); }
                    catch (e) { fail(e); }
                  }}>Read</button>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {topics && (
        <div className="card">
          <h3>What the help box can answer</h3>
          <p className="muted small">{topics.disclosure}</p>
          <div className="row">
            {topics.topics.map((t) => (
              <span key={t} className="chip">{t.replace(/_/g, " ")}</span>
            ))}
          </div>
          <p className="muted small">
            Written answers, matched by keyword. They work whether or not a
            model is reachable — a help system that stops helping when a
            provider is down is absent on the day everything else is confusing
            too.
          </p>
        </div>
      )}

      {faces && (
        <div className="card">
          <h3>The pane that follows you</h3>
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
                  setNote(`${r.title} — ${r.path} (screen ${r.screen})`);
                  if (me && token) setFace(await api.dockFace(me, name, token));
                } catch (e) { fail(e); }
              }}>Where does it go?</button>
            </div>
          ))}

          {/* The more interesting half of the catalogue. */}
          {Object.entries(faces.refused).map(([name, why]) => (
            <p key={name} className="small">
              <strong>{name}</strong> — refused. {why}
            </p>
          ))}

          {dock && (
            <>
              <h4>Yours</h4>
              <p className="muted small">
                {dock.corner} · {dock.state} · showing {dock.face}
                {!dock.set && " — the default; you have not chosen yet"}
                {dock.tucked && dock.why && <> · tucked here: {dock.why}</>}
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
                  ? "This face can act."
                  : "It shows and never acts."}{" "}
                Never carries: {face.never.join(", ")}.
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
