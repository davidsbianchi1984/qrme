// One profile's bound voice, piece by piece — the reply starts being
// heard at its first sentence.
//
// Field report, and its twin product's the same week: "still a long
// delay while waiting for a response." The synthesis leg of that wait
// was being paid in full — the whole reply turned into one utterance
// before a word of it played. Cutting at sentence ends (pieces.ts) lets
// the first sentence be synthesised alone, small and therefore fast,
// while every later piece is fetched behind the piece already playing.
//
// A side effect that is really the point: each piece is far below any
// engine's synthesis ceiling, so a long reply no longer falls out of
// the bound voice into the browser's robot just for being long.
import { api } from "./api";
import { spokenPieces } from "./pieces";

export interface Speaking {
  /** Resolves when the speaking is over — played out, stopped, or died. */
  done: Promise<void>;
  /** Cut it off: the playing piece pauses and the rest are dropped. */
  stop: () => void;
}

/** Speak `text` in a profile's bound voice, pipelined by sentence.
 *
 *  Rejects only when the FIRST piece cannot be fetched — no binding, no
 *  engine — so a caller's device-voice fallback still has the whole text
 *  to speak. A LATER piece failing drops the remainder quietly instead:
 *  the text is standing on screen, and a reply that changes voices
 *  mid-sentence is stranger than one that stops. */
export async function speakInPieces(
  profileId: string, text: string, token: string,
): Promise<Speaking> {
  const pieces = spokenPieces(text);
  if (pieces.length === 0) {
    return { done: Promise.resolve(), stop: () => {} };
  }
  // Awaited before the handle exists: a caller that cannot get even the
  // first piece should take its fallback path, not hold a dead handle.
  const first = await api.sayInProfileVoice(profileId, pieces[0], token);
  let stopped = false;
  let current: HTMLAudioElement | null = null;
  const done = (async () => {
    let upNext: Promise<Blob | null> = Promise.resolve(first);
    for (let i = 0; i < pieces.length; i++) {
      const blob = await upNext.catch(() => null);
      if (blob === null || stopped) return;
      upNext = i + 1 < pieces.length
        ? api.sayInProfileVoice(profileId, pieces[i + 1], token)
        : Promise.resolve(null);
      const src = URL.createObjectURL(blob);
      const sound = new Audio(src);
      current = sound;
      await new Promise<void>((over) => {
        // `pause` is stop(); `ended` a played-out piece; `error` a decode
        // dying mid-utterance; a rejected play() (autoplay withheld after
        // all) ends the piece quietly. Any of them is the piece being over.
        sound.addEventListener("ended", () => over(), { once: true });
        sound.addEventListener("pause", () => over(), { once: true });
        sound.addEventListener("error", () => over(), { once: true });
        sound.play().catch(() => over());
      });
      URL.revokeObjectURL(src);
      current = null;
      if (stopped) return;
    }
  })();
  return {
    done,
    stop: () => { stopped = true; current?.pause(); },
  };
}
