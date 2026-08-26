// The room's second ear: a microphone this console actually owns.
//
// The first ear is the browser's own `SpeechRecognition` — live, free, no
// account and no round trip, and the right path everywhere it works. On iOS
// the constructor exists and the service always refuses, so the phone this
// product is mostly used on has a microphone button and no way to speak.
// Reported twice.
//
//     asked     can this browser hear you
//     mattered  can this browser reach a transcriber
//
// Recording brings three things the recogniser never could, and only one of
// them is the iPhone:
//
//   * `echoCancellation` — the browser's own AEC, on a stream we opened.
//     The room's echo defences were a 70%-word-overlap text match (misses a
//     misheard echo) and a clock (misses a late one). AEC works on the sound
//     itself, which is the only one of the three that is about the actual
//     problem: a speaker bleeding into a microphone.
//   * an analyser, which is what tells a person leaning in from a speaker
//     across the table — so barge-in can come back instead of being traded
//     away wholesale.
//   * a path that does not care what speech service the browser ships.
//
// It is a fallback and not a replacement. A deployment with no transcriber
// answers 503 and the recogniser stays the ordinary way in.
import { api } from "./api";
import { micClosed } from "./spoken";

/** A recording in progress. `stop` ends it early; `done` resolves with the
 *  words, or rejects with whatever the door said. */
export interface Recording {
  stop: () => void;
  done: Promise<string>;
}

/** True where this console can record at all. Separate from whether it
 *  *should*: a browser with a working recogniser uses that instead. */
export function canRecord(): boolean {
  return typeof navigator !== "undefined"
    && !!navigator.mediaDevices?.getUserMedia
    && typeof MediaRecorder !== "undefined";
}

/** How long a person's silence means they have finished saying it. The
 *  same 2.5s the sibling product settled on after a reviewer sent back
 *  five seconds as "still a long delay while waiting for a response". */
export const SILENCE_ENDS_MS = 2500;

/** What counts as a voice in a quiet room, out of 128. */
export const QUIET_FLOOR = 6;

/** And what it takes while the room is speaking. Interrupting means
 *  speaking up, which is what interrupting a person means too. A speaker
 *  across the table rarely clears this; a mouth near the microphone does
 *  easily. */
export const BARGE_PEAK = 22;

/** Record one turn and hand back what was said.
 *
 *  `speakingNow` is asked on every tick rather than passed once: the room
 *  starts and stops talking while this recording is open, and a threshold
 *  fixed at the moment the microphone opened would be the wrong one for
 *  most of the turn.
 */
export async function recordTurn(
  roomId: string, interactorId: string, token: string,
  speakingNow: () => boolean,
  onLevel?: (level: number) => void,
  onBarge?: () => void,
): Promise<Recording> {
  return open(async (blob) => {
    const heard = await api.heardInRoom(roomId, interactorId, blob, token);
    return (heard.text || "").trim();
  }, speakingNow, onLevel, undefined, onBarge);
}

/** The same ear pointed at a conversation instead of a room: one recorded
 *  turn, transcribed through `/interactors/{id}/heard`. The chat overlay,
 *  its dictation bar and the studio orb fall back to this when the
 *  browser's recogniser exists but cannot reach its speech service — the
 *  handheld's report: `network` on every start, a microphone with no
 *  transcriber behind it. */
export async function recordAsked(
  interactorId: string, token: string,
  onLevel?: (level: number) => void,
  quietEndsMs?: number,
): Promise<Recording> {
  return open(
    async (blob) => (await api.heard(interactorId, blob, token)).trim(),
    () => false, onLevel, quietEndsMs);
}

/** The recording itself, held apart from the door the words go through.
 *
 *  `quietEndsMs`, when given, ends a take that never heard a voice at all
 *  after that many milliseconds. Without it a fully silent take runs
 *  forever — the silence clock below only starts once something voiced has
 *  been heard — which is fine for a room waiting for anyone to speak, and
 *  exactly wrong for a conversation where the empty take IS the signal:
 *  the talk face's auto-send waits on that take ending, and a person who
 *  finished their sentence stood at "Listening…" with a Send button they
 *  were promised they would not need. Opt-in per caller, because only the
 *  caller knows whether its silence means "nothing yet" or "go". */
async function open(
  transcribe: (blob: Blob) => Promise<string>,
  speakingNow: () => boolean,
  onLevel?: (level: number) => void,
  quietEndsMs?: number,
  onBarge?: () => void,
): Promise<Recording> {
  const stream = await navigator.mediaDevices.getUserMedia({
    // Asked for by name rather than hoped for. This is the one echo
    // defence that works on sound instead of on words or on clocks.
    audio: { echoCancellation: true, noiseSuppression: true,
             autoGainControl: true },
  });

  const chunks: BlobPart[] = [];
  const rec = new MediaRecorder(stream);
  rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };

  let watcher = 0;
  let ctx: AudioContext | null = null;
  // Whether a voice-level sound was ever heard. A transcriber invents words
  // out of silence — the sibling product watched a specialist answer "thank
  // you" to an empty room, each invented turn resetting the idle clock. A
  // recording the analyser never saw cross the threshold never reaches the
  // door at all.
  let voiced = false;
  let watched = false;
  let bargeFired = false;

  const stopWatching = () => {
    if (watcher) { window.clearInterval(watcher); watcher = 0; }
    if (ctx) { void ctx.close().catch(() => {}); ctx = null; }
    onLevel?.(0);
  };

  try {
    const w = window as unknown as {
      AudioContext?: typeof AudioContext;
      webkitAudioContext?: typeof AudioContext;
    };
    const Ctx = w.AudioContext ?? w.webkitAudioContext;
    if (Ctx) {
      ctx = new Ctx();
      watched = true;
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      ctx.createMediaStreamSource(stream).connect(analyser);
      const wave = new Uint8Array(analyser.fftSize);
      const born = Date.now();
      let lastVoice = Date.now();
      watcher = window.setInterval(() => {
        analyser.getByteTimeDomainData(wave);
        let peak = 0;
        for (let i = 0; i < wave.length; i++) {
          const dev = Math.abs(wave[i] - 128);
          if (dev > peak) peak = dev;
        }
        onLevel?.(Math.min(1, peak / 40));
        const bar = speakingNow() ? BARGE_PEAK : QUIET_FLOOR;
        if (peak > bar) { voiced = true; lastVoice = Date.now(); }
        // Somebody leaning in over the room's voice, read off THIS
        // recording's own analyser. The meter (below) does the same job
        // for the recogniser path with a second stream — but a platform
        // that allows one live capture at a time (iOS) mutes the first
        // stream when a second opens, so on the recorded path the barge
        // has to come from the one stream that is already standing.
        // Once per take, like the meter: interrupting is a thing you do,
        // not a state you enter.
        if (!bargeFired && speakingNow() && peak > BARGE_PEAK) {
          bargeFired = true;
          onBarge?.();
        }
        if (voiced && Date.now() - lastVoice > SILENCE_ENDS_MS) {
          if (rec.state !== "inactive") rec.stop();
        }
        // A take that heard nothing ends too, where the caller asked it
        // to — its rejection ("nothing was heard in that") is the very
        // signal the talk face's auto-send waits on.
        if (!voiced && quietEndsMs && Date.now() - born > quietEndsMs) {
          if (rec.state !== "inactive") rec.stop();
        }
      }, 100);
    }
  } catch {
    // No analyser on this platform: the recording still works, it simply
    // ends on the tap rather than on the silence, and everything recorded
    // goes to the door because there is nothing here that could tell.
  }

  const done = new Promise<string>((said, refused) => {
    rec.onstop = async () => {
      stopWatching();
      stream.getTracks().forEach((t) => t.stop());
      // The earbud starts its climb back to music mode here, not at the
      // button press — spoken.ts holds the reply's first piece until the
      // climb has had its second (the mode-switch grace).
      micClosed();
      const blob = new Blob(chunks, { type: rec.mimeType || "audio/webm" });
      if (!blob.size) { refused(new Error("nothing was recorded")); return; }
      // The energy gate. A platform with no analyser cannot tell, so it
      // asks rather than assuming — the old behaviour, kept for it alone.
      if (watched && !voiced) {
        refused(new Error("nothing was heard in that"));
        return;
      }
      try {
        said(await transcribe(blob));
      } catch (e) { refused(e as Error); }
    };
  });

  rec.start();
  return {
    stop: () => { if (rec.state !== "inactive") rec.stop(); },
    done,
  };
}

/** Listen for somebody leaning in while the room is speaking.
 *
 *  The gap the recorded ear does not cover. On a browser with a working
 *  recogniser — Chrome, Edge, everything but Safari — the room listens
 *  through that recogniser, which has no analyser behind it and cannot tell
 *  a person raising their voice from the speaker across the table. So the
 *  echo fix had to drop EVERYTHING heard while the room was speaking, and
 *  barge-in went with it. That trade was reported the same day it shipped:
 *  the profile keeps talking over you.
 *
 *      asked     was that sound the room's own voice
 *      mattered  or somebody interrupting it
 *
 *  A meter answers it. This opens a microphone stream purely to measure
 *  level — nothing is recorded, nothing is sent — for exactly as long as the
 *  room's voice is in the air, and reports the moment somebody clears the
 *  bar an echo does not. The recogniser keeps doing the hearing; this only
 *  decides whether to believe it.
 *
 *  Returns a closer. Call it when the voice stops: a meter left open is a
 *  microphone light nobody asked to leave on.
 */
export async function meterWhileSpeaking(
  onBargeIn: () => void,
): Promise<() => void> {
  if (!canRecord()) return () => {};
  const w = window as unknown as {
    AudioContext?: typeof AudioContext;
    webkitAudioContext?: typeof AudioContext;
  };
  const Ctx = w.AudioContext ?? w.webkitAudioContext;
  if (!Ctx) return () => {};

  let stream: MediaStream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      // Echo cancellation here too, and for the sharper reason: without it
      // the speaker's own output is what the meter would measure, and every
      // sentence the room said would read as an interruption.
      audio: { echoCancellation: true, noiseSuppression: true },
    });
  } catch {
    return () => {};          // refused: no meter, and no barge-in either
  }

  const ctx = new Ctx();
  const analyser = ctx.createAnalyser();
  analyser.fftSize = 1024;
  ctx.createMediaStreamSource(stream).connect(analyser);
  const wave = new Uint8Array(analyser.fftSize);
  let fired = false;
  const watcher = window.setInterval(() => {
    analyser.getByteTimeDomainData(wave);
    let peak = 0;
    for (let i = 0; i < wave.length; i++) {
      const dev = Math.abs(wave[i] - 128);
      if (dev > peak) peak = dev;
    }
    // Once per turn. A person who interrupts has interrupted; saying so
    // forty times a second would be the same fact over and over.
    if (!fired && peak > BARGE_PEAK) { fired = true; onBargeIn(); }
  }, 100);

  return () => {
    window.clearInterval(watcher);
    stream.getTracks().forEach((t) => t.stop());
    void ctx.close().catch(() => {});
    // Same as the recorder above: the meter held a real microphone, and
    // the piece that plays next should wait out the earbud's switch.
    micClosed();
  };
}
