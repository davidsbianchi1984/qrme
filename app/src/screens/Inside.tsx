import { useEffect, useState } from "react";
import { api, type MicsHere, type RoomMsg } from "../api";
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
  }
  useEffect(load, [open, token]);

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
            {seats.map((s) => (
              <div key={s.id}
                   className={"rs-tile" + (talking === s.display ? " talking" : "")}>
                <span className="rs-face">
                  {(s.display || "?").split(/\s+/)
                    .map((w) => w[0]).join("").slice(0, 2)}
                </span>
                <span className="rs-name">{s.display}</span>
                <span className="muted small">
                  {s.kind === "person"
                    ? tr("ins.seat.person", lang) : tr("ins.seat.profile", lang)}
                </span>
              </div>
            ))}
          </div>
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
