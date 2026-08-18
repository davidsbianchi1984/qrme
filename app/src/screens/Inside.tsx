import { useEffect, useRef, useState } from "react";
import { api, getBase, type Avatar, type MicsHere, type RoomFaces,
         type RoomMsg } from "../api";
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
// What a worn mask draws over your own preview, per catalogue kind. Your
// pixels never leave this device — the other seats show an on-air marker,
// not your stream — so the wearer's preview is the only place a mask can
// render at all, and until this map existed it rendered nowhere: the mask
// machinery recorded the disclosure and drew nothing, which read as broken.
//
// The glyph rides the box, not your facial landmarks. That is the honest
// budget of a beta with no face tracking, and the disclosure line stays the
// truth-bearing part. Three kinds are treatments of the video itself and
// carry a CSS class instead; `backdrop` would need segmentation this beta
// does not have, so it stays disclosure-only.
const MASK_GLYPHS: Record<string, string> = {
  mask: "\u{1F3AD}", half_mask: "\u{1F978}", character: "\u{1F9B9}",
  creature: "\u{1F98A}", puppet: "\u{1FA86}", avatar_2d: "\u{1F5BC}\uFE0F",
  avatar_3d: "\u{1F5FF}", helmet_hud: "\u{1FA96}", paint: "\u{1F3A8}",
  makeup: "\u{1F484}", hair: "\u{1F9D4}", headwear: "\u{1F3A9}",
  eyewear: "\u{1F576}\uFE0F", prosthetic: "\u{1F47A}",
  stylised: "\u{1F58C}\uFE0F",
};
const MASK_TREATMENTS: Record<string, string> = {
  obscured: " rs-obscured", silhouette: " rs-silhouette",
  touch_up: " rs-touchup",
};

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
  // The room's own channel, read off the join answer. `chat`, `voice` and
  // `video` present flat; `ar` and `vr` are the two the homepage sells as
  // *places*, and until this state existed the screen rendered them as the
  // same flat grid — the channel was a badge on the way in and nothing
  // inside. The scene card offers a stage for both now.
  const [channel, setChannel] = useState("");
  // The immersive stage. Entered by a press and left by one — never on the
  // room's behalf, because going fullscreen and turning sensors on are
  // decisions a person makes, not properties a room has.
  const [immersed, setImmersed] = useState(false);
  // VR look direction: degrees of yaw, driven by dragging the stage. The
  // seats sit on a turntable this angle turns.
  const [yaw, setYaw] = useState(0);
  const dragFrom = useRef<{ x: number; yaw: number } | null>(null);
  // AR passthrough — the device's world-facing camera as the stage floor.
  // Deliberately separate from the room-face camera machinery: this stream
  // renders your surroundings to you and only you, shares no fact with the
  // room, and stops the moment you step out.
  const pass = useRef<HTMLVideoElement>(null);
  const passStream = useRef<MediaStream | null>(null);
  const [passDenied, setPassDenied] = useState(false);
  const [masks, setMasks] = useState<
    { kind: string; covers_face: boolean; means: string }[]>([]);
  // The synthetic seats' portraits. `GET /profiles/{id}/avatar` is the one
  // shape every surface reads — 2-D, 3-D, VR, AR — and it carries the AI
  // badge and the likeness record with the picture, so this screen cannot
  // show the face without having been handed the disclosure. Until this map
  // existed a profile seat drew two initials while the platform held a whole
  // portrait for it, which read as "my agent has no avatar".
  const [aiFaces, setAiFaces] = useState<Record<string, Avatar>>({});
  const picker = useRef<HTMLInputElement>(null);
  // Which of the device's cameras. "user" is the selfie side; flipping asks
  // for the other and the effect below re-acquires the stream.
  const [facing, setFacing] = useState<"user" | "environment">("user");
  // Whether the controls are shown over a live full-bleed camera. A camera
  // that fills its box leaves nowhere for buttons to live politely, so they
  // hide — and a double-tap or a long press brings them back. Both gestures,
  // because neither is discoverable and two chances beat one.
  const [reveal, setReveal] = useState(false);
  const hold = useRef<number | null>(null);
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
    api.joinRoom(open, token)
      .then((r) => { setSeats(r.participants); setChannel(r.channel); })
      .catch(() => setSeats([]));
    // What is in the seats, and who is wearing what — one call, because a
    // second one would draw a frame with a face and no disclosure on it.
    api.roomFaces(open, token).then(setScene).catch(() => setScene(null));
  }
  useEffect(load, [open, token]);

  useEffect(() => {
    api.overlayCatalogue().then((c) => setMasks(c.kinds)).catch(() => setMasks([]));
  }, []);

  useEffect(() => {
    for (const seat of seats) {
      if (seat.kind === "user" || aiFaces[seat.id]) continue;
      api.avatar(seat.id, token)
        .then((a) => setAiFaces((m) => ({ ...m, [seat.id]: a })))
        .catch(() => undefined);
    }
    // aiFaces deliberately not a dep: it is the cache this effect fills.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seats, token]);

  const showing = scene?.faces[me]?.showing || "voice";

  // The camera itself. Held in a ref rather than state because a MediaStream
  // is a live handle, not a value to re-render on — and stopping every track
  // is the only thing that puts the device's own light out.
  useEffect(() => {
    let dropped = false;
    if (showing === "camera") {
      // A flip re-runs this effect, so the old side is stopped before the
      // new one is asked for — two live tracks is two camera lights.
      stream.current?.getTracks().forEach((t) => t.stop());
      stream.current = null;
      navigator.mediaDevices?.getUserMedia(
        // `ideal` rather than `exact`: a laptop has no back camera, and a
        // hard constraint there turns the flip button into an error dialog.
        { video: { facingMode: { ideal: facing } } })
        .then((s) => {
          if (dropped) { s.getTracks().forEach((t) => t.stop()); return; }
          stream.current = s;
          if (mine.current) mine.current.srcObject = s;
        })
        .catch((e) => setError(e));
    }
    if (showing !== "camera") {
      stream.current?.getTracks().forEach((t) => t.stop());
      stream.current = null;
      if (mine.current) mine.current.srcObject = null;
      setReveal(false);
    }
    return () => { dropped = true; };
  }, [showing, facing]);

  // Leaving the screen with a camera still running is how an indicator light
  // stays on in somebody's room after they have gone.
  useEffect(() => () => {
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
  }, []);

  // The AR passthrough, alive exactly while the stage is. The refusal path
  // matters as much as the grant: a denied camera downgrades the stage to
  // the flat backdrop and says so, rather than presenting a black room as
  // though that were the feature.
  useEffect(() => {
    if (!(immersed && channel === "ar")) {
      passStream.current?.getTracks().forEach((t) => t.stop());
      passStream.current = null;
      if (pass.current) pass.current.srcObject = null;
      return;
    }
    let gone = false;
    setPassDenied(false);
    navigator.mediaDevices?.getUserMedia(
      { video: { facingMode: { ideal: "environment" } } })
      .then((s) => {
        if (gone) { s.getTracks().forEach((t) => t.stop()); return; }
        passStream.current = s;
        if (pass.current) pass.current.srcObject = s;
      })
      .catch(() => setPassDenied(true));
    return () => {
      gone = true;
      passStream.current?.getTracks().forEach((t) => t.stop());
      passStream.current = null;
    };
  }, [immersed, channel]);

  /** What a seat shows at stage size: the photo somebody chose, a
   *  profile's own portrait with its AI mark, or the initials — the same
   *  resolution order the flat tiles use, because the stage is a way of
   *  standing in the room, not a different room. */
  const stageFace = (s: { kind: string; id: string; display: string }) => {
    const face = scene?.faces[s.id];
    if (face?.showing === "photo" && face.media_url) {
      return <img className="rs-photo" src={face.media_url} alt={s.display} />;
    }
    if (s.kind !== "user" && aiFaces[s.id]?.asset
        && !aiFaces[s.id]?.placeholder) {
      return <img className="rs-photo" alt={s.display}
                  src={(aiFaces[s.id].asset as string).startsWith("http")
                         ? (aiFaces[s.id].asset as string)
                         : getBase() + aiFaces[s.id].asset} />;
    }
    if (face?.showing === "camera") {
      return <span className="rs-face rs-oncam"
                   title={tr("ins.face.theirs", lang)}>
        {tr("ins.face.camicon", lang)}
      </span>;
    }
    return <span className="rs-face">
      {(s.display || "?").split(/\s+/).map((w) => w[0]).join("").slice(0, 2)}
    </span>;
  };

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
              const camLive = isMe && face?.showing === "camera";
              return (
              <div key={s.id}
                   className={"rs-tile" + (talking === s.display ? " talking" : "")
                              + (camLive ? " rs-camtile" : "")}
                   onDoubleClick={camLive
                     ? () => setReveal((v) => !v) : undefined}
                   onPointerDown={camLive ? () => {
                     hold.current = window.setTimeout(
                       () => setReveal((v) => !v), 550);
                   } : undefined}
                   onPointerUp={camLive ? () => {
                     if (hold.current) window.clearTimeout(hold.current);
                     hold.current = null;
                   } : undefined}
                   onPointerLeave={camLive ? () => {
                     if (hold.current) window.clearTimeout(hold.current);
                     hold.current = null;
                   } : undefined}>
                {/* What is in the box. A camera, a picture, or the initials —
                    and the box is the same size in all three, because the
                    quiet person is as present as the talking one. */}
                {isMe && face?.showing === "camera" ? (
                  <>
                    <video ref={mine}
                           className={"rs-live rs-fullbleed"
                             + (wearing
                                ? MASK_TREATMENTS[wearing.kind] || "" : "")}
                           autoPlay playsInline muted
                           aria-label={tr("ins.face.yourcamera", lang)} />
                    {wearing && MASK_GLYPHS[wearing.kind] && (
                      <span className="rs-mask" aria-hidden="true">
                        {MASK_GLYPHS[wearing.kind]}
                      </span>
                    )}
                    {!reveal && (
                      <span className="rs-hint">
                        {tr("ins.face.hint", lang)}
                      </span>
                    )}
                  </>
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
                ) : s.kind !== "user" && aiFaces[s.id]?.asset
                    && !aiFaces[s.id]?.placeholder ? (
                  // The profile's own portrait, in the same circle a person's
                  // photo uses. The AI mark on this tile is the disclosure the
                  // avatar route insists travels with the picture.
                  <img className="rs-photo" alt={s.display}
                       src={(aiFaces[s.id].asset as string).startsWith("http")
                              ? (aiFaces[s.id].asset as string)
                              : getBase() + aiFaces[s.id].asset} />
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
                {isMe && (!camLive || reveal) && (
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
                    {camLive && (
                      <button className="chip" disabled={busy}
                              onClick={() => setFacing(
                                (f) => f === "user" ? "environment" : "user")}>
                        {tr("ins.face.flip", lang)}
                      </button>
                    )}
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
          {/* The way into the stage, offered only in the rooms whose whole
              pitch is being a place. Flat rooms stay flat; nothing here
              turns a chat room into a headset demand. */}
          {(channel === "ar" || channel === "vr") && (
            <button disabled={busy} onClick={() => {
              setYaw(0); setImmersed(true);
            }}>
              {channel === "ar" ? tr("ins.stage.ar", lang)
                                : tr("ins.stage.vr", lang)}
            </button>
          )}
        </div>
      )}

      {immersed && (channel === "ar" || channel === "vr") && (
        // The stage: the same room, stood in. AR draws the seats over this
        // device's own passthrough; VR draws them around a turntable the
        // drag turns. Both are rendered here and only here — no pixels of
        // yours and no room of anybody else's crosses the wire for this.
        <div className={"room-stage" + (channel === "vr" ? " vr" : "")}
             role="dialog" aria-label={tr("ins.stage.title", lang)}
             onPointerDown={(e) => {
               dragFrom.current = { x: e.clientX, yaw };
             }}
             onPointerMove={(e) => {
               if (dragFrom.current == null) return;
               // A third of a degree per pixel: a full swipe across a phone
               // turns about 120° — enough to look around the circle without
               // a flick spinning the room.
               setYaw(dragFrom.current.yaw
                 + (e.clientX - dragFrom.current.x) / 3);
             }}
             onPointerUp={() => { dragFrom.current = null; }}
             onPointerLeave={() => { dragFrom.current = null; }}>
          {channel === "ar" && !passDenied && (
            <video ref={pass} className="stage-pass" autoPlay playsInline muted
                   aria-label={tr("ins.stage.passlabel", lang)} />
          )}
          {channel === "ar" && passDenied && (
            <p className="stage-note">{tr("ins.stage.denied", lang)}</p>
          )}
          {channel === "vr" && (
            <div className="stage-floor" aria-hidden="true" />
          )}
          {channel === "vr" ? (
            <div className="stage-turn">
              {seats.map((s, i) => {
                // The circle: seats spaced evenly, each card counter-rotated
                // so it faces the viewer from wherever the turntable stops —
                // a billboard, which is what a face is for.
                const a = (360 / Math.max(seats.length, 1)) * i;
                return (
                  <div key={s.id} className="stage-anchor"
                       style={{ transform:
                         `rotateY(${a + yaw}deg) translateZ(-280px)` }}>
                    <div className={"stage-seat"
                                    + (talking === s.display ? " talking" : "")}
                         style={{ transform: `rotateY(${-(a + yaw)}deg)` }}>
                      {stageFace(s)}
                      <span className="rs-name">{s.display}</span>
                      {s.kind !== "user" && (
                        <span className="rs-ai"
                              title={tr("ins.seat.profile", lang)}>
                          {tr("ins.seat.aimark", lang)}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            seats.map((s, i) => {
              // Anchored over the passthrough deterministically: the same
              // room shows everyone the same arrangement, because the seat
              // index — not a random draw — decides where a face floats.
              const n = Math.max(seats.length, 1);
              const left = 10 + (i * 80) / n + (i % 2) * 6;
              const top = 24 + ((i * 29) % 42);
              return (
                <div key={s.id}
                     className={"stage-seat ar"
                                + (talking === s.display ? " talking" : "")}
                     style={{ left: `${left}%`, top: `${top}%` }}>
                  {stageFace(s)}
                  <span className="rs-name">{s.display}</span>
                  {s.kind !== "user" && (
                    <span className="rs-ai" title={tr("ins.seat.profile", lang)}>
                      {tr("ins.seat.aimark", lang)}
                    </span>
                  )}
                </div>
              );
            })
          )}
          {/* The last thing said rides the stage, so stepping in is not
              stepping out of the conversation. */}
          {transcript.length > 0 && (
            <p className="stage-line">
              <strong>{transcript[transcript.length - 1].from}</strong>
              {": "}{transcript[transcript.length - 1].content}
            </p>
          )}
          <p className="stage-note">
            {channel === "ar" ? tr("ins.stage.arnote", lang)
                              : tr("ins.stage.vrnote", lang)}
          </p>
          <button className="stage-leave"
                  onClick={() => setImmersed(false)}>
            {tr("ins.stage.leave", lang)}
          </button>
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
                {/* A profile turn can be heard in the voice its owner bound.
                    A press, never autoplay: the phone's rule and the room's
                    are the same — sound starts on a gesture. */}
                {m.sender_kind === "profile" && m.sender_id && (
                  <button className="chip" disabled={busy}
                          aria-label={tr("ins.hear", lang)}
                          onClick={() => {
                            api.sayInProfileVoice(m.sender_id as string,
                                                  m.content || "", token)
                              .then((blob) => {
                                const src = URL.createObjectURL(blob);
                                const sound = new Audio(src);
                                sound.onended = () =>
                                  URL.revokeObjectURL(src);
                                void sound.play();
                              })
                              .catch(setError);
                          }}>
                    🔊
                  </button>
                )}
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
