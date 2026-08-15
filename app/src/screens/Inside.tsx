import { useEffect, useRef, useState } from "react";
import { api, type MicsHere, type RoomFaces, type RoomMsg } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Inside a room.
 *
 * `Rooms` opens one and lists what is live. It could not put you in it: the
 * console had no way to read a transcript, say anything, let the profiles
 * take a turn, or lend them a microphone. Six routes, four of them behind
 * `api.ts` bindings that no screen called — which is exactly what
 * `test_a_binding_is_not_a_door.py` was written to find, and building this
 * one found two defects worth more than the screen.
 *
 * ## Who may speak, and who may read
 *
 * `POST /rooms/{id}/messages` took the speaker from `sender_id` **in the
 * body**, and checked only that the id named a participant — never that the
 * caller was that person. Anybody holding a room id could put words in a
 * named participant's mouth: stored under their name, rendered `from: Ada`,
 * and answered by every profile in the room as though she had spoken.
 *
 * `GET /rooms/{id}/messages` asked for nothing at all, so the whole
 * conversation was readable by anyone who knew the id.
 *
 * A room id is not a secret — it rides in beacons and on printed QR
 * stickers, which is the point of them. That sentence was already written
 * down two routes away, on `GET /rooms/{id}/mic`, guarding the *narrower*
 * fact: who is wearing a live microphone was held to a standard the
 * conversation itself was not.
 *
 * ## The microphone is a disclosure, not a setting
 *
 * Lending one is shown to everybody in the room, because a microphone
 * somebody else cannot see is the thing this feature exists not to be. The
 * list is rendered whether or not you are the lender.
 *
 * ## The box is where you decide what people see of you
 *
 * The scene drew everybody in their own box and a box held one thing: two
 * initials and a name. Three controls live on your own box now — your camera,
 * a picture you upload, and the mask machinery `overlays` has owned since it
 * shipped and which was reachable only from a screen where you type a surface
 * name and a room id by hand.
 *
 * All three states are a box, at the same size, in the same place. A person
 * who has their camera off is still here, and a scene that shrinks or drops
 * them answers *who is talking* while losing *who is here*.
 *
 * **Only your own box carries controls.** Deciding what somebody else's box
 * shows is not something this product offers, and the route refuses it — but
 * a control that renders and then refuses is worse than one that is absent.
 */
export function Inside({ onPlans, start = "" }: {
  onPlans: () => void;
  /** A room id handed in by the Rooms screen's join — the field is
   *  prefilled so the person lands in the room they just entered. */
  start?: string;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [roomId, setRoomId] = useState(start);
  const [transcript, setTranscript] = useState<RoomMsg[]>([]);
  const [mics, setMics] = useState<MicsHere | null>(null);
  const [seats, setSeats] = useState<
    { kind: string; id: string; display: string }[]>([]);
  const [draft, setDraft] = useState("");
  const [scene, setScene] = useState<RoomFaces | null>(null);
  const [masks, setMasks] = useState<
    { kind: string; covers_face: boolean; means: string }[]>([]);
  const picker = useRef<HTMLInputElement>(null);
  // The local preview. Rendering is the device's, exactly as `overlays` says —
  // what the backend holds is the fact that a camera is on, which is what
  // lets everybody else's client draw the same scene.
  const mine = useRef<HTMLVideoElement>(null);
  const stream = useRef<MediaStream | null>(null);

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const open = roomId.trim();

  function load() {
    if (!open || !token) return;
    api.roomMessages(open, token).then(setTranscript).catch(setError);
    api.micsInRoom(open, token).then(setMics).catch(() => setMics(null));
    // The seats. Joining twice is being there once, so the join door
    // doubles as the who-is-here read — and going in renders a scene
    // rather than leaving you on the same form, which a field report
    // described as "it just stayed here in the same menu".
    api.joinRoom(open, token).then((r) => setSeats(r.participants))
      .catch(() => setSeats([]));
    // What is in the seats, and who is wearing what — one call, because a
    // second one would draw a frame with a face and no disclosure on it.
    api.roomFaces(open, token).then(setScene).catch(() => setScene(null));
  }
  useEffect(load, [open, token]);

  useEffect(() => {
    api.overlayCatalogue().then((c) => setMasks(c.kinds)).catch(() => setMasks([]));
  }, []);

  const showing = scene?.faces[me]?.showing || "voice";

  // The camera itself. Held in a ref rather than state because a MediaStream
  // is a live handle, not a value to re-render on — and stopping every track
  // is the only thing that puts the device's own light out.
  useEffect(() => {
    let dropped = false;
    if (showing === "camera" && !stream.current) {
      navigator.mediaDevices?.getUserMedia({ video: true })
        .then((s) => {
          if (dropped) { s.getTracks().forEach((t) => t.stop()); return; }
          stream.current = s;
          if (mine.current) mine.current.srcObject = s;
        })
        .catch((e) => setError(e));
    }
    if (showing !== "camera" && stream.current) {
      stream.current.getTracks().forEach((t) => t.stop());
      stream.current = null;
      if (mine.current) mine.current.srcObject = null;
    }
    return () => { dropped = true; };
  }, [showing]);

  // Leaving the screen with a camera still running is how an indicator light
  // stays on in somebody's room after they have gone.
  useEffect(() => () => {
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
  }, []);

  // Whose square is lit: the last voice in the transcript. `from` carries
  // the display name each seat also carries.
  const talking = transcript.length > 0
    ? transcript[transcript.length - 1].from : null;

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  const lentByMe = mics?.microphones_lent.some((m) => m.interactor_id === me);

  return (
    <div className="screen">
      <h2>{tr("ins.title", lang)}</h2>
      <p className="muted small">{tr("ins.pitch", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("ins.whichroom", lang)}</h3>
        <div className="row">
          <input value={roomId} onChange={(e) => setRoomId(e.target.value)}
                 placeholder={tr("ins.roomid.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !open || !token} onClick={act(async () => {
            load();
          })}>
            {tr("ins.goin", lang)}
          </button>
        </div>
        {!token && (
          <p className="muted small">{tr("ins.signinperson", lang)}</p>
        )}
      </div>

      {open && seats.length > 0 && (
        // The scene: everyone in the room in their own square, and the
        // square of whoever spoke last wears the light. The transcript
        // stays below — the scene is where you are, the transcript is
        // what was said.
        <div className="card">
          <h3>{tr("ins.scene", lang)}</h3>
          <div className="room-scene">
            {seats.map((s) => {
              const face = scene?.faces[s.id];
              const isMe = s.kind === "user" && s.id === me;
              const wearing = scene?.wearing.find(
                (w) => w.interactor_id === s.id);
              return (
              <div key={s.id}
                   className={"rs-tile" + (talking === s.display ? " talking" : "")}>
                {/* What is in the box. A camera, a picture, or the initials —
                    and the box is the same size in all three, because the
                    quiet person is as present as the talking one. */}
                {isMe && face?.showing === "camera" ? (
                  <video ref={mine} className="rs-live" autoPlay playsInline
                         muted aria-label={tr("ins.face.yourcamera", lang)} />
                ) : face?.showing === "camera" ? (
                  // Somebody else's camera. The fact is shared; the pixels
                  // are not — this product carries no stream between clients,
                  // and drawing a fake frame here would be the one lie the
                  // whole scene is built to avoid.
                  <span className="rs-face rs-oncam"
                        title={tr("ins.face.theirs", lang)}>
                    {tr("ins.face.camicon", lang)}
                  </span>
                ) : face?.showing === "photo" && face.media_url ? (
                  <img className="rs-photo" src={face.media_url}
                       alt={s.display} />
                ) : (
                  <span className="rs-face">
                    {(s.display || "?").split(/\s+/)
                      .map((w) => w[0]).join("").slice(0, 2)}
                  </span>
                )}
                <span className="rs-name">{s.display}</span>
                {/* The mark, top left, on the synthetic seats and no others —
                    the way the screen this is drawn from does it, and the way
                    the rest of the platform does it.

                    It replaces a caption underneath that read `person` against
                    a field the backend spells `user`, so the ternary never
                    matched and every human in the room was labelled a profile
                    — on the one screen where telling the two apart is the
                    entire point. The word is kept as the title so it is still
                    readable, and so the person's own word is still spoken to
                    a screen reader. */}
                {s.kind === "user" ? (
                  <span className="sr-only">{tr("ins.seat.person", lang)}</span>
                ) : (
                  <span className="rs-ai" title={tr("ins.seat.profile", lang)}>
                    {tr("ins.seat.aimark", lang)}
                  </span>
                )}
                {/* The mask disclosure, on the face it is about. It rides with
                    the scene rather than sitting in a settings screen nobody
                    opens — the sentence is addressed to the other people. */}
                {wearing && (
                  <span className="muted small rs-worn">
                    {wearing.disclosure}
                  </span>
                )}
                {isMe && (
                  <div className="rs-controls">
                    <button className="chip" disabled={busy}
                            aria-pressed={face?.showing === "camera"}
                            onClick={act(async () => {
                              await api.setRoomFace(
                                open, me,
                                face?.showing === "camera" ? "voice" : "camera",
                                token);
                            })}>
                      {face?.showing === "camera"
                        ? tr("ins.face.cameraoff", lang)
                        : tr("ins.face.cameraon", lang)}
                    </button>
                    <button className="chip" disabled={busy}
                            onClick={() => picker.current?.click()}>
                      {tr("ins.face.photo", lang)}
                    </button>
                    <input ref={picker} type="file" accept="image/*"
                           style={{ display: "none" }}
                           onChange={(e) => {
                             const file = e.target.files?.[0];
                             e.target.value = "";
                             if (file) {
                               act(async () => {
                                 await api.uploadRoomFace(open, me, file, token);
                               })();
                             }
                           }} />
                    {/* Off, back to a name in a box — which is still a box.
                        Offered only when there is something to take down. */}
                    {face && face.showing !== "voice" && (
                      <button className="chip" disabled={busy}
                              onClick={act(async () => {
                                await api.clearRoomFace(open, me, token);
                              })}>
                        {tr("ins.face.plain", lang)}
                      </button>
                    )}
                    {/* The masks. Two records, not one: taking a mask off and
                        turning a camera off are different actions, so this
                        sits beside the three above rather than among them. */}
                    <select className="chip" disabled={busy}
                            value={wearing?.kind || ""}
                            onChange={(e) => {
                              const kind = e.target.value;
                              act(async () => {
                                if (!kind) {
                                  await api.takeOffOverlay("room", open, me,
                                                           token);
                                  return;
                                }
                                const said = masks.find((m) => m.kind === kind);
                                await api.wearOverlay("room", open, {
                                  interactor_id: me, kind,
                                  title: said?.means || kind,
                                }, token);
                              })();
                            }}>
                      <option value="">{tr("ins.face.nomask", lang)}</option>
                      {masks.map((m) => (
                        <option key={m.kind} value={m.kind}>{m.means}</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
              );
            })}
          </div>
          {scene && <p className="muted small">{scene.note}</p>}
        </div>
      )}

      {open && (
        <>
          <div className="card">
            <h3>{tr("ins.whatsaid", lang)}</h3>
            {transcript.length === 0 && (
              <p className="muted small">{tr("ins.nothingyet", lang)}</p>
            )}
            {transcript.map((m) => (
              <p className="small" key={m.id}>
                <strong>{m.from}</strong>: {m.content}
                {/* A profile's turn is always watermarked and a person's
                    never is, so the mark is the honest way to tell which
                    kind of speaker this was — not the name. */}
                {m.watermark?.display?.line && (
                  <span className="muted small">
                    {" "}· {m.watermark.display.line}
                  </span>
                )}
              </p>
            ))}
            <div className="row">
              <input value={draft} onChange={(e) => setDraft(e.target.value)}
                     placeholder={tr("ins.say.ph", lang)} style={{ flex: 1 }} />
              <button disabled={busy || !token || !draft.trim()}
                      onClick={act(async () => {
                        const text = draft;
                        setDraft("");
                        await api.sayInRoom(open, me, text, token);
                      })}>
                {tr("ins.sayit", lang)}
              </button>
              <button disabled={busy || !token}
                      onClick={act(async () => {
                        await api.advanceRoom(open, token);
                      })}>
                {tr("ins.letthemtalk", lang)}
              </button>
            </div>
            <p className="muted small">{tr("ins.watermarked", lang)}</p>
          </div>

          <div className="card">
            <h3>{tr("ins.microphones", lang)}</h3>
            {mics && <p className="muted small">{mics.note}</p>}
            {mics?.microphones_lent.map((m) => (
              <p className="small" key={m.interactor_id}>
                {fill(tr("ins.micline", lang), {
                  who: <code>{m.interactor_id}</code>, device: m.device,
                  hears: m.hears, when: m.since,
                })}
              </p>
            ))}
            <div className="row">
              {!lentByMe ? (
                <button disabled={busy || !token || !me}
                        onClick={act(async () => {
                          await api.lendMicInRoom(open, me, token);
                        }, tr("ins.lent", lang))}>
                  {tr("ins.lendmic", lang)}
                </button>
              ) : (
                <button disabled={busy || !token}
                        onClick={act(async () => {
                          await api.takeBackMicInRoom(open, me, token);
                        }, tr("ins.takenback", lang))}>
                  {tr("ins.takeback", lang)}
                </button>
              )}
            </div>
            <p className="muted small">{tr("ins.micpitch", lang)}</p>
          </div>
        </>
      )}
    </div>
  );
}
