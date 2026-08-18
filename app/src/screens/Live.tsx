import { useEffect, useState } from "react";
import { api, type Bystanders, type CameraDisclosure, type CameraSession,
         type CameraVocabulary, type MicPlaces, type MicVocabulary,
         type MicsHere, type OverlayCatalogue, type OverlaysHere,
         type WhosePlace } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * What is live in a shared place — a camera being shared, a microphone lent
 * to the profiles in a room, a face drawn over a camera.
 *
 * Twenty routes with no caller: three features that look separate and are
 * one. The same rule holds all of them together, and it is the rule this
 * screen exists to show:
 *
 *   **Whatever you put between yourself and the people around you, they are
 *   told.**
 *
 * A camera session lists what a viewer can never do — no zoom, no capture, no
 * other cameras, no coordinates, no standing permission, and no state where it
 * is running and hidden from the holder's own screen. A microphone may only be
 * one you wear, only near-field, and *"everyone in the room is shown that you
 * lent it"*. An overlay says *"a real person is underneath"* and names every
 * wearer.
 *
 * Three things here are rendered verbatim rather than summarised, because each
 * is an argument the backend already made carefully and a paraphrase would be
 * a worse version of it:
 *
 * - the `never` list on a camera session;
 * - the refusal when a profile is asked to watch a person's body, which is a
 *   whole paragraph about accountability and is the most important sentence in
 *   this feature;
 * - `why_it_is_yours` on the bystander note — the platform declines to promise
 *   anything about who walked into shot, because it cannot see the room, and
 *   saying so is more honest than a reassurance it could not keep.
 */
export function Live({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [cam, setCam] = useState<CameraVocabulary | null>(null);
  const [mic, setMic] = useState<MicVocabulary | null>(null);
  const [places, setPlaces] = useState<MicPlaces | null>(null);
  const [overlays, setOverlays] = useState<OverlayCatalogue | null>(null);

  const [live, setLive] = useState<CameraSession[]>([]);
  const [bys, setBys] = useState<Bystanders | null>(null);
  const [subject, setSubject] = useState("object");
  const [viewerKind, setViewerKind] = useState("person");
  const [viewerId, setViewerId] = useState("");

  // Two pickers, not one. The camera and the microphone accept *different*
  // sets of surfaces — a watch party can take a lent microphone and cannot
  // take a shared camera, and a room is the other way round (it takes a
  // camera, and lends microphones through its own route). Driving them
  // against a real server is what surfaced that; a single picker built from
  // one vocabulary 422s on half its own options.
  const [camSurface, setCamSurface] = useState("room");
  const [camSurfaceId, setCamSurfaceId] = useState("");
  // Real places to point the pickers at. Typing a raw id was the whole of
  // the old form, and the field report called it what it was.
  const [myRooms, setMyRooms] = useState<
    { id: string; topic?: string | null }[]>([]);
  const [surface, setSurface] = useState("party");
  const [surfaceId, setSurfaceId] = useState("");
  const [whose, setWhose] = useState<WhosePlace | null>(null);
  const [disclosure, setDisclosure] = useState<CameraDisclosure | null>(null);
  const [mics, setMics] = useState<MicsHere | null>(null);
  const [worn, setWorn] = useState<OverlaysHere | null>(null);
  const [overlayKind, setOverlayKind] = useState("mask");
  const [overlayTitle, setOverlayTitle] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.cameraVocabulary().then((v) => {
      setCam(v);
      setSubject(Object.keys(v.subjects)[0] || "object");
      setCamSurface(Object.keys(v.surfaces)[0] || "room");
    }).catch(fail);
    api.micVocabulary().then(setMic).catch(() => undefined);
    api.micPlaces().then((p) => {
      setPlaces(p);
      setSurface(p.places[0]?.surface || "party");
    }).catch(() => undefined);
    api.overlayCatalogue().then((c) => {
      setOverlays(c);
      setOverlayKind(c.kinds[0]?.kind || "mask");
    }).catch(() => undefined);
    api.listRooms().then(setMyRooms).catch(() => setMyRooms([]));
  }, []);

  // The bystander note is per subject kind, because the honest answer
  // differs: a boiler has no face, a room full of people does.
  useEffect(() => {
    if (!subject) return;
    api.bystanders(subject).then(setBys).catch(() => setBys(null));
  }, [subject]);

  useEffect(() => {
    if (!me || !token) return;
    api.liveCameras(me, token).then(setLive).catch(() => setLive([]));
  }, [me, token]);

  function loadPlace() {
    if (!surfaceId.trim() || !token) return;
    setError(null);
    const id = surfaceId.trim();
    api.whosePlace(surface, id, token).then(setWhose).catch(() => setWhose(null));
    api.cameraDisclosure(surface, id, token).then(setDisclosure)
      .catch(() => setDisclosure(null));
    api.micsHere(surface, id, token).then(setMics).catch(() => setMics(null));
    api.overlaysHere(surface, id, token).then(setWorn).catch(() => setWorn(null));
  }

  const mayWatch = cam && cam.may_watch[subject]?.[viewerKind];

  return (
    <div className="screen">
      <h2>{tr("liv.title", lang)}</h2>
      <p className="muted small">{tr("liv.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("liv.share", lang)}</h3>
        <div className="row">
          <select value={subject} onChange={(e) => setSubject(e.target.value)}>
            {cam && Object.keys(cam.subjects).map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select value={viewerKind}
                  onChange={(e) => setViewerKind(e.target.value)}>
            {cam?.viewers.map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
          <input value={viewerId} onChange={(e) => setViewerId(e.target.value)}
                 placeholder={tr("liv.who.ph", lang)} style={{ flex: 1 }} />
        </div>
        <p className="muted small">
          {fill(tr("liv.subjectline", lang), {
            means: cam?.subjects[subject]?.means,
            risk: cam?.subjects[subject]?.bystander_risk,
          })}
        </p>

        {/* The refusal, in full, before the button rather than after it. */}
        {cam && mayWatch === false && (
          <div className="card error">
            <p className="small">{cam.refusals.profile_on_person}</p>
          </div>
        )}

        <div className="row">
          {/* The camera's own surfaces, which are not the microphone's. */}
          <select value={camSurface}
                  onChange={(e) => setCamSurface(e.target.value)}>
            {cam && Object.keys(cam.surfaces).map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          {camSurface === "room" && myRooms.length > 0 ? (
            <select value={camSurfaceId} style={{ flex: 1 }}
                    onChange={(e) => setCamSurfaceId(e.target.value)}>
              <option value="">{tr("liv.where.ph", lang)}</option>
              {myRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.topic || r.id}
                </option>
              ))}
            </select>
          ) : (
            <input value={camSurfaceId}
                   onChange={(e) => setCamSurfaceId(e.target.value)}
                   placeholder={tr("liv.where.ph", lang)} style={{ flex: 1 }} />
          )}
          <button disabled={!token || !viewerId.trim() || !camSurfaceId.trim()
                            || mayWatch === false}
                  onClick={async () => {
            setError(null); setNote(null);
            try {
              await api.openCamera({
                holder_id: me, viewer_id: viewerId.trim(),
                viewer_kind: viewerKind, subject,
                surface: camSurface, surface_id: camSurfaceId.trim(),
                minutes: cam?.default_minutes,
              }, token);
              setNote(tr("liv.livenow.said", lang));
              api.liveCameras(me, token).then(setLive).catch(() => undefined);
              loadPlace();
            } catch (e) { fail(e); }
          }}>{tr("liv.startsharing", lang)}</button>
        </div>
        {cam && (
          <p className="muted small">
            {fill(tr("liv.upto", lang), {
              surface: cam.surfaces[camSurface],
              n: cam.max_minutes,
              rec: cam.records_by_default
                ? tr("liv.recording", lang) : tr("liv.notrecording", lang),
            })}
          </p>
        )}
      </div>

      {/* Whose problem the room is, said plainly. */}
      {bys && (
        <div className="card">
          <h3>{tr("liv.bystanders", lang)}</h3>
          <p className="small">{bys.risk}</p>
          <p className="muted small">
            {fill(tr("liv.wecannot", lang), { what: bys.we_cannot })}
          </p>
          <p className="muted small">
            {fill(tr("liv.youcan", lang), { what: bys.you_can })}
          </p>
          <p className="muted small"><em>{bys.why_it_is_yours}</em></p>
        </div>
      )}

      {live.length > 0 && (
        <div className="card">
          <h3>{tr("liv.camon", lang)}</h3>
          {live.map((s) => (
            <div key={s.id}>
              <div className="row">
                <div style={{ flex: 1 }}>
                  <strong>{s.subject}</strong> — {s.subject_means}
                  <div className="muted small">
                    {fill(tr("liv.camline", lang), {
                      surface: s.surface, id: s.surface_id,
                      minutes: s.minutes,
                      rec: s.recording
                        ? tr("liv.recording", lang)
                        : tr("liv.notrecording", lang),
                    })}
                  </div>
                </div>
                <button onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    await api.closeCamera(s.id, me, token);
                    setNote(tr("liv.stopped.said", lang));
                    api.liveCameras(me, token).then(setLive).catch(() => undefined);
                  } catch (e) { fail(e); }
                }}>{tr("liv.stop", lang)}</button>
              </div>
              {/* Verbatim: the six things the person watching cannot do. */}
              <ul className="small">
                {Object.entries(s.never).map(([k, v]) => (
                  <li key={k}>{v}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>{tr("liv.lookplace", lang)}</h3>
        <div className="row">
          <select value={surface} onChange={(e) => setSurface(e.target.value)}>
            {places?.places.map((p) => (
              <option key={p.surface} value={p.surface}>{p.surface}</option>
            ))}
          </select>
          <input value={surfaceId} onChange={(e) => setSurfaceId(e.target.value)}
                 placeholder={tr("liv.id.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!token || !surfaceId.trim()} onClick={loadPlace}>
            {tr("liv.look", lang)}
          </button>
        </div>
        <p className="muted small">
          {places?.places.find((p) => p.surface === surface)?.why}
        </p>
        {/* Rooms lend through their own route, and the reply says so. */}
        {places && <p className="muted small">{places.room}</p>}
        {whose && (
          <p className="small">
            {fill(tr("liv.whose", lang), {
              who: whose.display_name || whose.account_id, is: whose.is })}
          </p>
        )}
        {disclosure && (
          <p className="small">
            {disclosure.note}
            {disclosure.any_recording &&
              <strong> {tr("liv.somethingrec", lang)}</strong>}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("liv.lendmic", lang)}</h3>
        {mic && (
          <>
            <ul className="small">{mic.rules.map((r) => <li key={r}>{r}</li>)}</ul>
            <p className="muted small">
              {fill(tr("liv.worn", lang),
                { what: mic.personal.join(", ") })}
            </p>
            {/* One reason, repeated for every refused device, and it is the
                reason that matters: their voices are not yours to lend. */}
            {mic.refusals[0] && (
              <p className="muted small">
                {fill(tr("liv.refused", lang), {
                  kinds: mic.refusals.map((r) => r.kind).join(", "),
                  why: mic.refusals[0].why,
                })}
              </p>
            )}
          </>
        )}
        {mics && (
          <>
            <p className="small">{mics.note}</p>
            {mics.microphones_lent.map((m) => (
              <div key={m.interactor_id} className="row">
                <div style={{ flex: 1 }}>
                  <strong>{m.device}</strong>
                  <div className="muted small">
                    {fill(tr("liv.micline", lang), {
                      gain: m.gain, hears: m.hears, since: m.since })}
                  </div>
                </div>
                {m.interactor_id === me && (
                  <button onClick={async () => {
                    setError(null); setNote(null);
                    try {
                      await api.takeBackMicHere(surface, surfaceId.trim(), me, token);
                      setNote(tr("liv.takenback.said", lang));
                      loadPlace();
                    } catch (e) { fail(e); }
                  }}>{tr("liv.takeback", lang)}</button>
                )}
              </div>
            ))}
          </>
        )}
        <button disabled={!token || !surfaceId.trim()} onClick={async () => {
          setError(null); setNote(null);
          try {
            const r = await api.lendMicHere(surface, surfaceId.trim(), me, token);
            setNote(r.note);
            loadPlace();
          } catch (e) { fail(e); }
        }}>{tr("liv.lendmine", lang)}</button>
      </div>

      <div className="card">
        <h3>{tr("liv.wear", lang)}</h3>
        <div className="row">
          <select value={overlayKind}
                  onChange={(e) => setOverlayKind(e.target.value)}>
            {overlays?.kinds.map((k) => (
              <option key={k.kind} value={k.kind}>{k.kind}</option>
            ))}
          </select>
          <input value={overlayTitle}
                 onChange={(e) => setOverlayTitle(e.target.value)}
                 placeholder={tr("liv.callit.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!token || !surfaceId.trim() || !overlayTitle.trim()}
                  onClick={async () => {
            setError(null); setNote(null);
            try {
              const o = await api.wearOverlay(surface, surfaceId.trim(), {
                interactor_id: me, kind: overlayKind,
                title: overlayTitle.trim(),
              }, token);
              // The sentence everybody else in the place sees.
              setNote(o.disclosure);
              setOverlayTitle("");
              loadPlace();
            } catch (e) { fail(e); }
          }}>{tr("liv.wearit", lang)}</button>
        </div>
        <p className="muted small">
          {overlays?.kinds.find((k) => k.kind === overlayKind)?.means}
        </p>
        {worn && (
          <>
            <p className="small">{worn.note}</p>
            {worn.overlays.map((o) => (
              <div key={o.id} className="row">
                <div style={{ flex: 1 }}>
                  <strong>{o.title}</strong>
                  <div className="muted small">{o.disclosure}</div>
                </div>
                {o.interactor_id === me && (
                  <button onClick={async () => {
                    setError(null); setNote(null);
                    try {
                      await api.takeOffOverlay(surface, surfaceId.trim(), me, token);
                      setNote(tr("liv.takenoff.said", lang));
                      loadPlace();
                    } catch (e) { fail(e); }
                  }}>{tr("liv.takeoff", lang)}</button>
                )}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
