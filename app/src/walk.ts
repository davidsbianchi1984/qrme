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
  /** What it is called, with its designation in front where it has one —
   *  the strip names it the way every other surface has to. */
  shownName: string;
  /** The voice the reply is read in, so walking sounds like the screen. */
  lang: string;
  /** How this conversation takes a turn.
   *
   * A callback rather than an id, because the four surfaces that can be
   * carried do not share a wire: a synthetic profile answers through
   * `POST /profiles/{id}/chat`, QRME's agent through the authoring turn,
   * and JIM's two through its own coach. Holding the ids here would have
   * meant the strip knowing all four, and a fifth surface meaning a fifth
   * branch inside it.
   *
   *     asked     can the strip carry this conversation
   *     mattered  does the strip have to know what kind it is
   *
   * The screen that started the walk already knows how to take its own
   * turn. It hands that over and the strip stays ignorant, which is what
   * lets it be one component instead of four.
   */
  take: (message: string) => Promise<Said>;
};

/** What a turn came back as, and who answered it.
 *
 * A turn used to be a string, which was enough until somebody asked what
 * happens when the deployment has no model. The answer is that it already
 * works — the offline stack answers from stored knowledge — and the person
 * was never told, so text written by a fallback read exactly like text
 * written by the model they chose.
 *
 *     asked     did the turn come back
 *     mattered  who wrote it
 *
 * `offline` is set by the screen that knows its own wire, from what that
 * wire reports. The strip only renders it: a component that inferred who
 * answered would be guessing about somebody else's endpoint.
 */
export type Said = {
  text: string;
  /** True when the answer came from what is stored here rather than from a
   *  model. Never a failure — an answer is an answer — but never silent
   *  either. */
  offline?: boolean;
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
