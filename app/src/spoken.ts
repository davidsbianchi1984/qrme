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

/** The element a voice is playing through right now, or null.
 *
 *  Exposed for the face: a 3-D head's mouth is driven from the sound
 *  already in the air (`Avatar3D`), which means the renderer needs the
 *  element itself rather than a copy of the audio. One element, shared —
 *  a second fetch of the same speech to animate a jaw would be a second
 *  bill for a sound the room already has.
 */
export function nowPlaying(): HTMLAudioElement | null {
  return ear && !ear.paused ? ear : null;
}

// ------------------------------------------------------------------------
// Loudness: full blast by default, dialled DOWN by the person.
//
// Field report, from an earbud: the voice worked and was hard to hear. Two
// decisions came out of it. The default is 1.0 — the loudest a page may
// play — because a quiet default helps nobody and the device's own volume
// rocker is the ceiling anyway. And the slider only attenuates: a boost
// above 1.0 means clipping, which reads as a broken voice, not a loud one.
//
// The other half of that report is not a setting: a page holding a
// Bluetooth earbud's MICROPHONE drops the earbud from its music mode into
// phone-call mode — quiet and tinny at any volume. The play-only paths in
// this module (`playClip`, `speakInPieces`, `plainVoice`) therefore open
// no microphone, ever. The talk surfaces' barge-in meter is the one
// deliberate exception, and it belongs to those surfaces, not to playback.
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// The mode-switch grace.
//
// The loudness comment above ends at "open no microphone, ever" — but a
// Bluetooth earbud that has JUST given its microphone back is not yet out
// of phone-call mode: the switch back to music mode takes it a second or
// two, and a reply that starts the instant the mic closes plays its first
// words into the tail of that switch — quiet and tinny, or clipped — even
// though nothing holds the mic any more.
//
// So the paths that do hold a microphone (roomear, the walking strip, the
// dictation meter) report the moment they let it go, and the play paths
// below wait out what remains of the grace before the FIRST piece only.
// Pieces after the first ride an earbud already back in music mode and
// wait for nothing — and the first piece's synthesis fetch runs DURING
// the grace, so on the ordinary turn most of the wait was already being
// paid to the network and nobody notices the rest.
//
//     asked     does the reply start promptly
//     mattered  does its first sentence arrive in the mode the rest of
//               it will play in
// ------------------------------------------------------------------------

/** A second or two, per the field report; the low end of it, because the
 *  grace only delays a reply when the mic closed under two seconds ago
 *  and the fetch has not already covered the gap. */
const MIC_GRACE_MS = 1500;

let micClosedAt = 0;

/** A surface that held a microphone just let it go. Call it where the
 *  tracks actually stop — not where a button was pressed, which can be
 *  seconds earlier. */
export function micClosed(): void {
  micClosedAt = Date.now();
}

/** Resolves once the earbud has had its switch back. Instant almost
 *  always: whenever no mic closed within the grace window. */
function afterMicGrace(): Promise<void> {
  const left = MIC_GRACE_MS - (Date.now() - micClosedAt);
  return left > 0
    ? new Promise((go) => window.setTimeout(go, left))
    : Promise.resolve();
}

const LOUDNESS_KEY = "qrme.loudness";

function storedLoudness(): number {
  try {
    const v = parseFloat(localStorage.getItem(LOUDNESS_KEY) ?? "1");
    return Number.isFinite(v) ? Math.min(1, Math.max(0.05, v)) : 1;
  } catch {
    return 1;
  }
}

let loudness = storedLoudness();

/** How loud the spoken voice plays, 0.05–1. 1 is the default and the max. */
export function spokenLoudness(): number {
  return loudness;
}

/** Set it, remember it on this device, and apply it to the element that is
 *  already speaking — a slider that only affects the NEXT sentence reads
 *  as broken while this one is in your ear. */
export function setSpokenLoudness(v: number): void {
  loudness = Math.min(1, Math.max(0.05, v));
  try { localStorage.setItem(LOUDNESS_KEY, String(loudness)); } catch { /* per-device nicety */ }
  if (ear) ear.volume = loudness;
}


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
let earOpen = false;

export function openTheEar(): void {
  // The OTHER voice needs the gesture too: iOS ignores a speechSynthesis
  // call that never rode a press — silently, no error, the utterance
  // simply never starts. An empty utterance spoken here, inside the real
  // gesture, unlocks the device voice the way play() unlocks the element.
  try {
    if (typeof speechSynthesis !== "undefined") {
      speechSynthesis.speak(new SpeechSynthesisUtterance(""));
    }
  } catch { /* a platform with no synthesiser has nothing to unlock */ }
  if (earOpen) return;
  const el = ear ?? new Audio(SILENCE);
  // Muted so the silence cannot even theoretically be heard, and inline
  // so iOS does not hand playback to its own full-screen player. A refused
  // attempt no longer leaves a dead element standing — the sibling product
  // found that `if (ear) return` made the first refusal the last try, and
  // on an iPhone the first try being refused is the ordinary case.
  el.muted = true;
  el.setAttribute("playsinline", "");
  if (!el.src) el.src = SILENCE;
  el.volume = loudness;
  ear = el;
  el.play().then(() => { el.pause(); el.muted = false; earOpen = true; },
                () => { el.muted = false; });
}

/** Open the ear on presses anywhere on the page.
 *
 *  Armed once, at import, rather than wired into each screen's press
 *  handlers — a list of gesture sites that must all remember to call
 *  something is a list with one missing entry, which here means one
 *  screen silent on a phone and nowhere else. The first cut listened on
 *  pointerdown and removed itself after the first press whether or not
 *  the platform granted anything; WebKit counts the tail of the gesture
 *  (click, touchend), so on an iPhone the one press this ever took was
 *  one the platform refused. These listeners stay attached until an
 *  attempt actually succeeds, and the explicit calls at Send and the
 *  microphones stay — they are the presses a reply rides on. */
function armTheEar(): void {
  if (typeof document === "undefined") return;
  const open = () => {
    openTheEar();
    if (earOpen) {
      document.removeEventListener("click", open, true);
      document.removeEventListener("touchend", open, true);
      document.removeEventListener("keydown", open, true);
    }
  };
  document.addEventListener("click", open, true);
  document.addEventListener("touchend", open, true);
  document.addEventListener("keydown", open, true);
}
armTheEar();

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
    el.volume = loudness;
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
    await afterMicGrace();
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
  // reach the caller as a rejection while it can still fall back. The
  // grace sits after the fetch on purpose — the network already ran
  // during the earbud's switch, so this usually waits for nothing.
  await afterMicGrace();
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

// ------------------------------------------------------------------------
// Sensing what is connected.
//
// Field report, asked for by name: "you shouldn't have to go there [the
// settings menus] to be using something that's already connected to your
// device and you're primarily using." The voice should come out of the
// earbud that is already in the person's ear, including the one that
// connects mid-conversation.
//
// Two halves. The follower below re-pins the one playing element to the
// system's current default output whenever the set of devices changes —
// on the platforms that let a page choose at all (`setSinkId`; Chrome,
// Edge). The platforms that refuse (iOS, Safari) route every element to
// the system default themselves, which is the same behaviour arrived at
// from the other side — so the follower simply does nothing there rather
// than existing as a broken switch. And `hearingThrough` names the device
// the voice is on, for a screen that wants to SAY it — empty wherever the
// platform hides device labels (they unlock with mic permission), because
// a guessed name on a settings screen is worse than no line.
// ------------------------------------------------------------------------

type Sinkable = HTMLAudioElement & { setSinkId?: (id: string) => Promise<void> };

function followTheDefault(): void {
  if (typeof navigator === "undefined") return;
  navigator.mediaDevices?.addEventListener?.("devicechange", () => {
    const el = ear as Sinkable | null;
    // "" is the spec's name for "the system default, whatever it now is".
    // Re-asserting it moves a piece already in the air onto the earbud
    // that just connected — the mid-sentence case a person actually hits.
    if (el?.setSinkId) void el.setSinkId("").catch(() => { /* kept: system routing */ });
  });
}
followTheDefault();

/** The name of the output the voice plays through, or "" where the
 *  platform withholds it. Ask again on `devicechange` — the answer moves
 *  with the earbud. */
export async function hearingThrough(): Promise<string> {
  try {
    const devs = await navigator.mediaDevices.enumerateDevices();
    const outs = devs.filter((d) => d.kind === "audiooutput");
    const def = outs.find((d) => d.deviceId === "default") ?? outs[0];
    // Chrome labels the default "Default - <name>"; the person's word for
    // it is the <name>.
    return (def?.label ?? "").replace(/^default( -|:)?\s*/i, "");
  } catch {
    return "";
  }
}

/** The device's own voice, awaited.
 *
 * What stands in when `speakInPieces` rejects — no binding, no engine, or a
 * platform that refused to play. It is a worse voice and it is not silence,
 * which is the whole of the argument for it.
 *
 * Awaited on purpose. A caller that reopens a microphone when speaking
 * *starts* rather than when it ends records its own reply, which is what a
 * field report on Windows watched the walking strip do.
 */
export function plainVoice(text: string, lang: string): Promise<void> {
  if (!("speechSynthesis" in window)) return Promise.resolve();
  return afterMicGrace().then(() => new Promise((done) => {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    u.volume = loudness;
    // The hang that held a lock: an utterance iOS declines to start fires
    // neither `end` nor `error` — it is simply never spoken — and a caller
    // awaiting it waits forever. The room's reply queue wedged behind
    // exactly this. If the platform has not STARTED the voice within three
    // seconds, the promise settles and the caller moves on.
    let began = false;
    const watchdog = window.setTimeout(() => { if (!began) done(); }, 3000);
    u.onstart = () => { began = true; };
    u.onend = () => { window.clearTimeout(watchdog); done(); };
    u.onerror = () => { window.clearTimeout(watchdog); done(); };
    window.speechSynthesis.speak(u);
  }));
}
