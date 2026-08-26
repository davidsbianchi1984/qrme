// What the conversation is doing, and what the avatar should therefore be.
//
// The avatar is not the synthetic profile. The profile is identity, memory,
// personality, relationship, permission and adaptive state; the avatar is the
// presentation of that profile's *current* state on one particular surface.
// This module is the seam between the two, so a renderer never reaches into
// the conversation and the conversation never knows what is drawing it.
//
//     asked     is the character on screen
//     mattered  does it show what is happening
//
// Before this, the talk surface had one boolean — `listening` — and used it
// for the pulse, the caption and nothing else. A profile that was thinking,
// speaking, or had just failed looked identical to one sitting idle, so the
// only honest thing the screen could say was "tap to talk".

/** The states a conversation can be in, named for what a person can observe
 *  rather than for what the code is doing. `thinking` is the pause after
 *  they stop talking; `processing` is work that is not a reply — a document
 *  being read, an import being distilled. */
export type Presence =
  | "idle" | "listening" | "thinking" | "speaking"
  | "paused" | "processing" | "error";

export const PRESENCE: Presence[] = [
  "idle", "listening", "thinking", "speaking",
  "paused", "processing", "error",
];

/** The conversation facts a presence is derived from. Deliberately not the
 *  conversation object itself: this takes what it needs and nothing more, so
 *  a screen with a different shape of state can still use it. */
export interface ConversationSignals {
  listening?: boolean;
  /** A turn is out and the reply has not arrived. */
  awaiting?: boolean;
  /** Audio is being played back — the profile is talking. */
  speaking?: boolean;
  /** Work that is not a reply: an import being read, a file distilled. */
  working?: boolean;
  /** Set when the last thing that happened was a failure. */
  failed?: boolean;
  /** The surface is open but deliberately not listening. */
  held?: boolean;
}

/** One place decides, so the caption, the glow, the waveform and the
 *  animation can never disagree about what is happening.
 *
 * Order is the priority order, and it is not arbitrary: a failure outranks
 * everything because a screen that shows `speaking` over a failed turn is
 * lying about the most important thing on it. Speaking outranks listening
 * because the ear now stays open through the profile's whole reply — that
 * is what lets a person interrupt — so "listening" would be the caption for
 * the entire turn and the person would never see that the profile is
 * talking. The moment they do interrupt, playback stops, `speaking` drops,
 * and the caption is "listening" again: the floor still changes hands, it
 * just changes hands on the audio rather than on the flag. */
export function presenceOf(s: ConversationSignals): Presence {
  if (s.failed) return "error";
  if (s.speaking) return "speaking";
  if (s.listening) return "listening";
  if (s.awaiting) return "thinking";
  if (s.working) return "processing";
  if (s.held) return "paused";
  return "idle";
}

/** Whether the waveform should be moving, and on whose audio.
 *
 *  The waveform was permanently animated in the design it came from, which
 *  makes it decoration. Tied to presence it is a reading: bars that move
 *  when nobody is speaking say the microphone is live when it is not. */
export function waveformOf(p: Presence): "in" | "out" | "busy" | "still" {
  if (p === "listening") return "in";      // their voice, coming in
  if (p === "speaking") return "out";      // the profile's, going out
  if (p === "thinking" || p === "processing") return "busy";
  return "still";
}

/** Whether the figure should animate at all in this state. Kept separate
 *  from the waveform because a calm default is the point: the spec asks for
 *  states, not for a character that never stops moving. */
export function animatedIn(p: Presence): boolean {
  return p === "listening" || p === "speaking" || p === "thinking";
}

/** The l10n key for the line under the figure. One key per state, so a
 *  translator sees the whole set rather than a sentence assembled at the
 *  call site. */
export function presenceKey(p: Presence): string {
  return `talk.state.${p}`;
}

// --------------------------------------------------------------------------
// The renderer the presentation kind calls for
// --------------------------------------------------------------------------

/** How this surface will actually draw the avatar.
 *
 *  `still` is not a failure state — it is the honest answer for a kind this
 *  console does not render. A model attached by its owner is on the record
 *  and reaching every surface; the console showing the still and saying so
 *  is better than the console rendering the poster and letting the owner
 *  believe their model is on screen. Same call `ProfilePageView` makes about
 *  a stranger's markup: name the gap rather than paper over it.
 *
 *  There is no `orb`. A profile with no portrait yet gets the empty frame,
 *  and it gets it from `render()` rather than from here — one answer, decided
 *  in one place, so no surface can invent a second. */
export type Renderer = "image" | "video" | "still";

/** What this console can run today. A kind absent from here falls back with
 *  a sentence rather than silently. */
const RENDERS: Record<string, boolean> = {
  image: true,
  video: true,
  // No 3-D runtime in this bundle, and no scene frame: a `<model-viewer>` is
  // a dependency and a scene is a stranger's page given somewhere to run,
  // which is the proposition the homepage sandbox already declines.
  model: false,
  scene: false,
};

export interface AvatarSource {
  kind?: string;
  asset?: string | null;
  torso?: string | null;
  still?: string | null;
  placeholder?: boolean;
}

/** `(renderer, src)` — what to draw and what to draw it from. */
export function rendererFor(a: AvatarSource | null | undefined):
    { renderer: Renderer; src: string | null } {
  if (!a) return { renderer: "image", src: null };
  const kind = a.kind || "image";
  // The frame is an image like any other, so `placeholder` no longer decides
  // *whether* to draw — only how to caption it. Treating it as "nothing to
  // draw" is what sent this surface looking for a fallback of its own.
  const face = a.torso || a.asset || null;
  if (RENDERS[kind]) {
    if (kind === "video") return { renderer: "video", src: a.asset || null };
    return { renderer: "image", src: face };
  }
  // A kind this surface cannot run. `still` is the backend's own answer for
  // what stands in; the frame is the floor under it.
  return { renderer: "still", src: a.still || a.torso || a.asset || null };
}
