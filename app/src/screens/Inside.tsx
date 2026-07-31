import { useEffect, useState } from "react";
import { api, type MicsHere, type RoomMsg } from "../api";
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
export function Inside({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [roomId, setRoomId] = useState("");
  const [transcript, setTranscript] = useState<RoomMsg[]>([]);
  const [mics, setMics] = useState<MicsHere | null>(null);
  const [draft, setDraft] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const open = roomId.trim();

  function load() {
    if (!open || !token) return;
    api.roomMessages(open, token).then(setTranscript).catch(setError);
    api.micsInRoom(open, token).then(setMics).catch(() => setMics(null));
  }
  useEffect(load, [open, token]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  const lentByMe = mics?.microphones_lent.some((m) => m.interactor_id === me);

  return (
    <div className="screen">
      <h2>Inside a room</h2>
      <p className="muted small">
        Read it, say something, let the profiles take a turn. You have to be
        in the room — knowing its id is not the same as being here, and the
        id travels on stickers.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Which room</h3>
        <div className="row">
          <input value={roomId} onChange={(e) => setRoomId(e.target.value)}
                 placeholder="room id, from Rooms" style={{ flex: 1 }} />
          <button disabled={busy || !open || !token} onClick={act(async () => {
            load();
          })}>
            Go in
          </button>
        </div>
        {!token && (
          <p className="muted small">
            Sign in as a person first — a room turn is spoken by somebody, so
            a profile's owner token is refused here by name.
          </p>
        )}
      </div>

      {open && (
        <>
          <div className="card">
            <h3>What has been said</h3>
            {transcript.length === 0 && (
              <p className="muted small">Nothing yet.</p>
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
                     placeholder="say something" style={{ flex: 1 }} />
              <button disabled={busy || !token || !draft.trim()}
                      onClick={act(async () => {
                        const text = draft;
                        setDraft("");
                        await api.sayInRoom(open, me, text, token);
                      })}>
                Say it
              </button>
              <button disabled={busy || !token}
                      onClick={act(async () => {
                        await api.advanceRoom(open, token);
                      })}>
                Let them talk
              </button>
            </div>
            <p className="muted small">
              Everything a profile says here is watermarked as synthetic
              media, at the moment it is said. A room with anybody under 18 in
              it runs strict moderation for everyone.
            </p>
          </div>

          <div className="card">
            <h3>Microphones</h3>
            {mics && <p className="muted small">{mics.note}</p>}
            {mics?.microphones_lent.map((m) => (
              <p className="small" key={m.interactor_id}>
                <code>{m.interactor_id}</code> · {m.device} · {m.hears} ·
                since {m.since}
              </p>
            ))}
            <div className="row">
              {!lentByMe ? (
                <button disabled={busy || !token || !me}
                        onClick={act(async () => {
                          await api.lendMicInRoom(open, me, token);
                        }, "Lent. Everyone here is shown that you did.")}>
                  Lend them my microphone
                </button>
              ) : (
                <button disabled={busy || !token}
                        onClick={act(async () => {
                          await api.takeBackMicInRoom(open, me, token);
                        }, "Taken back.")}>
                  Take my microphone back
                </button>
              )}
            </div>
            <p className="muted small">
              In a voice room your own microphone carries your voice to the
              other people; the profiles are reading text and have no ear.
              Lending yours gives them one — keyed to your voice and set
              narrow enough to reach only you, not the room. Everybody here is
              shown that you lent it, which is the whole point: a microphone
              the others cannot see is what this is built not to be.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
