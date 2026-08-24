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

/** iOS Safari is the exception, and it was found on a phone rather than
 * reasoned out here.
 *
 * A field report: walk, swipe up to the home screen, come back to Safari,
 * and the conversation had stopped without a word. iOS suspends the whole
 * page the moment you leave it — capture included — so `hears` buys nothing
 * there. It was written down as though it bought the same thing everywhere,
 * which is the kind of claim that reads as tested and is not.
 *
 *     asked     did the capture survive being put away
 *     mattered  does the strip find out when it did not
 *
 * The strip cannot know in advance which platform it is on and does not
 * guess. It checks on the way back, says so when the ear is gone, and
 * offers the way in again. For an iPhone specifically the real answer is
 * the native shell, which holds the microphone through the background audio
 * mode and shows the system's own orange dot.
 */
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
  /** How this conversation speaks, and it is the screen's own voice.
   *
   * The strip shipped calling `SpeechSynthesisUtterance` — the browser's
   * built-in robot — while the console next door had `spoken.ts` playing the
   * profile's own bound voice. A field report heard the robot and reasonably
   * assumed the voice key had broken; nothing had broken, the strip had
   * simply never asked.
   *
   *     asked     did the reply get spoken
   *     mattered  in whose voice
   *
   * A callback for the same reason `take` is one: the screen knows its own
   * profile and token, and the strip stays ignorant of both. It resolves
   * when the speaking has finished, which is also what tells the ear when it
   * may open again — see `hears`.
   */
  say?: (text: string) => Promise<void>;
  /** How this conversation hears, when it can hear in a way that survives
   *  the window being minimised.
   *
   * The browser's own recogniser is ended when a page is put away — that is
   * documented behaviour and `away.ts` was written about it. `getUserMedia`
   * is not, except on one platform: an open capture keeps recording
   * while the window is minimised on a desktop browser and on Android,
   * and the browser shows its own recording indicator throughout. So a strip
   * that wants to survive being minimised records and posts the bytes to be
   * turned into words, rather than listening.
   *
   *     asked     does a hidden page stop hearing
   *     mattered  which of the two ways of hearing was it using
   *
   * A callback for the same reason `take` is one: the ear needs the
   * person's own credential, and the screen is the only thing that has it.
   * Optional, because a surface with nobody signed in has no credential to
   * spend on transcription — and when it is missing the strip falls back to
   * the recogniser and says plainly that this one stops when the window
   * does, rather than quietly hearing nothing.
   */
  hears?: (audio: Blob) => Promise<string>;
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
