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
//
// ## Why a phone heard nothing at all
//
// Field report: "on the mobile device it's not playing voice audio
// whatsoever." Not the wrong voice, not a delay — nothing, and no error
// anywhere to say so.
//
// Two things together made that total and silent.
//
// A phone withholds autoplay unless the playback descends from a real
// press. Every piece here was a **fresh `new Audio()`**, constructed
// after an `await` on the synthesis fetch — so by the time `play()` was
// called the press that started the turn was long over, and each new
// element carried no activation of its own. A desktop browser allows it
// and a phone refuses it, which is exactly why this survived every
// round of testing on a laptop.
//
// And the refusal was swallowed: `play().catch(() => over())` treated
// "the platform refused" as "this piece is finished". The loop walked
// every sentence, played none, and resolved `done` like a reply that had
// been heard — so the callers' device-voice fallback, which exists for
// precisely this, was never reached. A caller cannot fall back from a
// success.
//
//     asked     did the platform play this
//     mattered  does anybody find out when it did not
//
// So: one element, unlocked inside a real press (`openTheEar`) and
// reused for every piece thereafter, and a first piece the platform
// refuses is a **rejection** — the same signal as a piece that could not
// be fetched, because to a listener they are the same event.
import { api } from "./api";
import { spokenPieces } from "./pieces";

export interface Speaking {
  /** Resolves when the speaking is over — played out, stopped, or died. */
  done: Promise<void>;
  /** Cut it off: the playing piece pauses and the rest are dropped. */
  stop: () => void;
  /** How much of it was actually heard, as text.
   *
   *  A reply is spoken sentence by sentence, so an interruption lands at a
   *  known place: everything before the piece in the air was heard, and
   *  everything after it was not. Somebody who cuts a profile off has heard
   *  a prefix of what it said, and the profile answering them next needs to
   *  know WHICH prefix — otherwise it carries on from a point the person
   *  never reached, or repeats what they already sat through.
   *
   *  The piece being played when the stop lands counts as heard: it started,
   *  so some of it reached the room. Rounding the other way would have the
   *  profile re-say a sentence the person interrupted precisely because
   *  they had heard enough of it. */
  heard: () => string;
}

/** A 44-byte WAV with no samples. Playing it is inaudible and instant;
 *  its only job is to be the thing the press plays. */
const SILENCE =
  "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=";

/** The one element every piece plays through, once a press has opened it. */
let ear: HTMLAudioElement | null = null;

/** Open the ear on the first press anywhere on the page.
 *
 *  Armed once, at import, rather than wired into each screen's press
 *  handlers. Three screens speak and each has several ways in — the room's
 *  Go in, its send, its microphone; the chat's send; the agent's orb — and
 *  a list of gesture sites that must all remember to call something is a
 *  list with one missing entry, which here means one screen that is silent
 *  on a phone and nowhere else. Any press will do, so this takes any press.
 *
 *  Capture phase, and never cancelled: it only reads that a press happened.
 *  It removes itself once the ear is open, so the cost is one listener for
 *  the first press of a session. */
function armTheEar(): void {
  if (typeof document === "undefined") return;
  const open = () => {
    openTheEar();
    document.removeEventListener("pointerdown", open, true);
    document.removeEventListener("keydown", open, true);
  };
  document.addEventListener("pointerdown", open, true);
  document.addEventListener("keydown", open, true);
}
armTheEar();

/** Open the ear, from inside a user gesture.
 *
 *  Must be called **synchronously** in a press handler — not after an
 *  `await`, which is where the gesture ends. A phone grants playback to
 *  an *element* a person started, and that grant outlives the gesture, so
 *  one element opened at the door plays every later piece without asking
 *  again. Constructing a new element per piece throws that grant away,
 *  which is what this product did until a phone heard nothing.
 *
 *  Safe to call on every press: opening an already-open ear is a no-op,
 *  and a platform that refuses even this leaves `ear` standing so that
 *  `speakInPieces` still reports honestly rather than pretending. */
export function openTheEar(): void {
  if (ear) return;
  const el = new Audio(SILENCE);
  // Muted so the silence cannot even theoretically be heard, and inline
  // so iOS does not hand playback to its own full-screen player.
  el.muted = true;
  el.setAttribute("playsinline", "");
  ear = el;
  el.play().then(() => { el.pause(); el.muted = false; },
                () => { el.muted = false; });
}

/** Play one piece through the opened ear, resolving when it is over.
 *
 *  Rejects only when the platform refuses to start it. `ended`, `pause`
 *  and `error` all mean the same thing to a caller — the piece is over —
 *  so they resolve; a refusal is the one outcome where nothing was heard
 *  and somebody needs to know. */
function playPiece(el: HTMLAudioElement, src: string): Promise<void> {
  return new Promise<void>((over, refused) => {
    // All three come off together, whichever fired. `{ once: true }` alone
    // would leave the two that did not fire attached to an element that
    // outlives the piece — one reused element and a reply of nine
    // sentences ends up with eighteen dead listeners, and the next piece's
    // `pause` calls a resolve belonging to a sentence already finished.
    const clear = () => {
      el.removeEventListener("ended", done);
      el.removeEventListener("pause", done);
      el.removeEventListener("error", done);
    };
    const done = () => { clear(); over(); };
    el.addEventListener("ended", done);
    el.addEventListener("pause", done);
    el.addEventListener("error", done);
    el.src = src;
    el.play().catch((why) => { clear(); refused(why); });
  });
}

/** Play one ready-made clip through the opened ear.
 *
 *  For the places that already hold a blob and just want it heard — the
 *  settings screen's *test this voice*, which had the same defect in one
 *  line: `new Audio(src)` after an await on the synthesis, so the press
 *  that asked to hear the voice was over before anything tried to play.
 *  On a laptop it spoke and on a phone the button did nothing at all.
 *
 *  Rejects when the platform refuses, so a caller can say so. */
export async function playClip(blob: Blob): Promise<void> {
  if (!ear) ear = new Audio();
  const src = URL.createObjectURL(blob);
  try {
    await playPiece(ear, src);
  } finally {
    URL.revokeObjectURL(src);
  }
}

/** Speak `text` in a profile's bound voice, pipelined by sentence.
 *
 *  Rejects when the FIRST piece cannot be fetched — no binding, no
 *  engine — or cannot be played, so a caller's device-voice fallback
 *  still has the whole text to speak. Those two used to be different:
 *  a fetch that failed rejected, and a platform that refused resolved as
 *  though the reply had been heard. A listener cannot tell them apart,
 *  so neither does this any more.
 *
 *  A LATER piece failing drops the remainder quietly instead: the text is
 *  standing on screen, and a reply that changes voices mid-sentence is
 *  stranger than one that stops. */
export async function speakInPieces(
  profileId: string, text: string, token: string,
): Promise<Speaking> {
  const pieces = spokenPieces(text);
  if (pieces.length === 0) {
    return { done: Promise.resolve(), stop: () => {}, heard: () => "" };
  }
  // Awaited before the handle exists: a caller that cannot get even the
  // first piece should take its fallback path, not hold a dead handle.
  const first = await api.sayInProfileVoice(profileId, pieces[0], token);
  // A screen that never opened the ear at a press still gets an element
  // — on a desktop it simply plays, and on a phone the refusal below is
  // reported rather than swallowed.
  if (!ear) ear = new Audio();
  const el = ear;
  let stopped = false;
  // Pieces that began playing. The first is counted where it starts below,
  // not here: this is a record of what reached the room, so a piece the
  // platform refused must not be in it.
  let said = 0;

  // The first piece is played before the handle exists, for the same
  // reason the first piece is fetched before it: a refusal here has to
  // reach the caller as a rejection while it can still fall back.
  const firstSrc = URL.createObjectURL(first);
  let playing = playPiece(el, firstSrc);
  try {
    // Started, not finished — awaiting the whole piece would put the
    // caller's "it is speaking" light on a sentence late.
    await Promise.race([playing, started(el)]);
    said = 1;
  } catch (why) {
    URL.revokeObjectURL(firstSrc);
    throw why;
  }

  const done = (async () => {
    let upNext: Promise<Blob | null> = pieces.length > 1
      ? api.sayInProfileVoice(profileId, pieces[1], token)
      : Promise.resolve(null);
    for (let i = 0; i < pieces.length; i++) {
      if (i > 0) {
        const blob = await upNext.catch(() => null);
        if (blob === null || stopped) return;
        upNext = i + 1 < pieces.length
          ? api.sayInProfileVoice(profileId, pieces[i + 1], token)
          : Promise.resolve(null);
        const src = URL.createObjectURL(blob);
        playing = playPiece(el, src);
        said = i + 1;
        try {
          await playing;
        } catch {
          // A later piece the platform refuses ends the speaking rather
          // than reaching for another voice mid-reply.
          URL.revokeObjectURL(src);
          return;
        }
        URL.revokeObjectURL(src);
      } else {
        await playing.catch(() => {});
        URL.revokeObjectURL(firstSrc);
      }
      if (stopped) return;
    }
  })();
  return {
    done,
    stop: () => { stopped = true; el.pause(); },
    heard: () => pieces.slice(0, said).join(" "),
  };
}

/** Resolves once the element is actually running.
 *
 *  `play()` resolves when playback has begun, but a piece that is only
 *  milliseconds long can finish first; `playing` covers the ordinary
 *  case and the race covers the short one. */
function started(el: HTMLAudioElement): Promise<void> {
  return new Promise<void>((go) => {
    el.addEventListener("playing", () => go(), { once: true });
  });
}
