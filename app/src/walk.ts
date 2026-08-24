// A conversation that keeps going while you move about the app.
//
// `{tab === "chat" && <Chat/>}` — the screen unmounts on every tab change,
// and the voice with it. That is correct for navigating away and wrong for
// walking away on purpose, which is the same event to React and a different
// event to the person: one means they left the conversation, the other means
// they took it with them.
//
//     asked     did the screen unmount
//     mattered  did the person mean to end the conversation
//
// So the conversation moves above the tab switch when — and only when — it
// is asked to. Nothing here starts on its own, and the ordinary teardowns
// stay exactly as they were: an ear that survives a screen has to be one
// somebody pressed a button to keep.
//
// ## What this does not do
//
// It does not survive the page being put away. `away.ts` says why in its own
// words: a backgrounded page has its recogniser ended by the browser, and no
// amount of state above a tab switch changes that. Walking is inside this
// application. Minimising the browser and keeping the microphone is a native
// shell's job, and belongs where a foreground service and its notification
// can be honest about it.

export type Walking = {
  /** The profile being talked to, and what it is called with its
   *  designation in front — the strip names it the way every other surface
   *  has to. */
  profileId: string;
  shownName: string;
  interactorId: string;
  interactorToken: string;
  /** The voice the reply is read in, so walking sounds like the screen. */
  lang: string;
};

let current: Walking | null = null;
const listeners = new Set<(w: Walking | null) => void>();

export function walking(): Walking | null {
  return current;
}

/** Take the conversation with you. Called from a button, never from an
 *  effect: an ear that outlives its screen without a press is the headless
 *  microphone the unmount teardowns exist to prevent. */
export function startWalking(w: Walking): void {
  current = w;
  listeners.forEach((f) => f(current));
}

export function stopWalking(): void {
  current = null;
  listeners.forEach((f) => f(current));
}

/** Subscribe. Returns the release — held for as long as the subscriber is
 *  mounted, for the same reason `whenPutAway` returns one. */
export function onWalk(f: (w: Walking | null) => void): () => void {
  listeners.add(f);
  return () => { listeners.delete(f); };
}
