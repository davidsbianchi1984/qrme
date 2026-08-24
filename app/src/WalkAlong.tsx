import { useEffect, useRef, useState } from "react";
import { putAway, whenPutAway } from "./away";
import { isEcho } from "./echo";
import { plainVoice } from "./spoken";
import { t as tr } from "./l10n";
import { onWalk, stopWalking, walking, type Walking } from "./walk";

/**
 * The conversation you took with you.
 *
 * Mounted once, above the tab switch, so it outlives the screen it started
 * on. Every ear in this console is torn down when its screen unmounts —
 * correctly, because a microphone left open on a screen that no longer
 * exists is a recording indicator nobody can account for. This one is the
 * exception, and it earns the exception by being pressed for: nothing starts
 * it but a button, it says on screen that it is listening, and the way to
 * end it is the first control on the strip.
 *
 *     asked     is the microphone open
 *     mattered  does the person know, and can they close it
 *
 * ## What it does not survive
 *
 * Being put away. `away.ts` is explicit: a backgrounded page has its timers
 * throttled, its audio suspended and its recogniser ended by the browser,
 * and none of that arrives as an error. So the strip asks the same two
 * questions every other ear here asks — am I away, tell me when that changes
 * — and says it has stopped rather than going on claiming to listen. That is
 * the whole of the honesty available on the web: walking is inside this
 * application, and a minimised browser is a native shell's problem.
 */
/** How long a recorded turn runs before it is sent to be heard.
 *
 * Long enough to hold a whole sentence and most of a thought, short enough
 * that a reply does not arrive a minute after the question. A hidden tab's
 * timers are throttled, so this is measured by the media pipeline rather
 * than by a countdown that a background tab would stretch.
 */
const SLICE_MS = 8000;

export function WalkAlong() {
  const [who, setWho] = useState<Walking | null>(walking());
  const [heard, setHeard] = useState("");
  const [said, setSaid] = useState("");
  // Who answered the last turn. Not an error state — an answer
  // from what is stored here is an answer — but a person hearing
  // it should know it was not the model they picked.
  const [offline, setOffline] = useState(false);
  const [listening, setListening] = useState(false);
  const [asleep, setAsleep] = useState(putAway());
  const [trouble, setTrouble] = useState("");
  const rec = useRef<{ stop: () => void } | null>(null);
  const wants = useRef(false);
  const turn = useRef(0);
  // The reply is playing. The ear must not open while it does — a field
  // report on Windows watched the strip transcribe its own answer and send
  // it back as the next thing the person said, because the recorder sliced
  // every few seconds whether or not anything was speaking.
  //
  //     asked     is the microphone open
  //     mattered  is anything else in the room already talking
  const saying = useRef(false);
  // And what was last said, so a slice that catches the tail of it can be
  // recognised for what it is rather than answered. Belt to the braces
  // above: echo cancellation and a closed ear both leak a little, and the
  // console has had `isEcho` for exactly this since the rooms grew ears.
  const lastSaid = useRef("");

  useEffect(() => onWalk(setWho), []);

  // The page going away closes the ear and says so. Coming back does not
  // reopen it: a microphone that restarts itself because a tab regained
  // focus is one nobody pressed for, which is the line this whole component
  // is on the right side of.
  // Being put away closes the recogniser and not the recorder, because the
  // browser closes one and not the other. The first draft closed both — it
  // read `away.ts` as a fact about hidden pages when it is a fact about the
  // Web Speech API — and so invented a failure for the path that had none.
  //
  //     asked     does a hidden page stop hearing
  //     mattered  which of the two ways of hearing was it using
  //
  // ## And what a phone did to that
  //
  // A field report, from an iPhone: walk, swipe up to the home screen, come
  // back to Safari, and the conversation had stopped without a word. iOS
  // Safari suspends the whole page the moment you leave it, capture and
  // all — the survival above is a desktop fact and an Android fact, and on
  // iOS it is simply false. The strip could not have known that in advance
  // and does not try to; what it must do is notice on the way back.
  //
  //     asked     did the capture survive being put away
  //     mattered  does the strip find out when it did not
  //
  // So returning checks whether the ear is really still open, and says so
  // when it is not. Stopping without a word is the failure this whole
  // component is written against, and a platform stopping it is no excuse
  // for the silence.
  useEffect(() => whenPutAway(
    () => { setAsleep(true); if (!walking()?.hears) close(); },
    () => {
      setAsleep(false);
      // A tick, because the recorder's own `onstop` may still be queued
      // behind the page waking up — reading `wants` in the same beat would
      // catch a teardown that has not finished announcing itself.
      window.setTimeout(() => {
        if (!walking()) return;
        if (!wants.current) {
          setListening(false);
          setTrouble(tr("walk.away.stopped", walking()!.lang as never));
        }
      }, 0);
    }), []);

  useEffect(() => {
    if (!who) { close(); return; }
    // The path that survives, by name, when the screen handed one over.
    // The recogniser is the fallback and says what it costs.
    if (who.hears) void record(who); else listen(who);
    return close;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [who?.shownName]);

  function close() {
    turn.current += 1;
    wants.current = false;
    const r = rec.current;
    rec.current = null;
    setListening(false);
    r?.stop();
  }

  /** The ear that survives a minimised window.
   *
   * `getUserMedia` keeps capturing while the page is hidden — an open
   * capture keeps the tab alive and the browser shows its own recording
   * indicator throughout — where the recogniser below is ended by the
   * browser without a word. So when the screen handed over a way to hear,
   * this is the path taken, and the other one is the fallback rather than
   * the default.
   *
   * A turn is a fixed slice rather than a silence detection, and that is a
   * concession to being hidden: a background tab's timers are throttled, so
   * an analyser watching for a pause would report it late and unevenly.
   * A slice arrives on the media pipeline's own schedule.
   */
  async function record(w: Walking) {
    if (!w.hears || rec.current) return;
    // Never under the reply. `turnTaken` calls this again once the speaking
    // has finished; opening here would put the microphone back into the
    // room the answer is still playing into.
    if (saying.current) return;
    const mine = ++turn.current;
    const live = () => mine === turn.current;
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true } });
    } catch {
      if (live()) { setListening(false); setTrouble(tr("walk.nomic", w.lang as never)); }
      return;
    }
    if (!live()) { stream.getTracks().forEach((t) => t.stop()); return; }
    const parts: BlobPart[] = [];
    const mr = new MediaRecorder(stream);
    mr.ondataavailable = (e) => { if (e.data.size) parts.push(e.data); };
    mr.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      if (!live()) return;
      const clip = new Blob(parts, { type: mr.mimeType || "audio/webm" });
      void heardClip(w, mine, clip);
    };
    rec.current = { stop: () => { try { mr.stop(); } catch { /* gone */ } } };
    wants.current = true;
    setListening(true);
    mr.start();
    window.setTimeout(() => { if (live()) rec.current?.stop(); }, SLICE_MS);
  }

  async function heardClip(w: Walking, mine: number, clip: Blob) {
    rec.current = null;
    let words = "";
    try {
      words = (await w.hears!(clip)).trim();
    } catch (e) {
      if (mine !== turn.current) return;
      // A deployment with no ears says so in its own sentence, and this is
      // the one place a person cannot see a screen to read it on — so it
      // ends the walk rather than looping silently.
      wants.current = false;
      setListening(false);
      setTrouble(e instanceof Error ? e.message
                                   : tr("walk.lost", w.lang as never));
      return;
    }
    if (mine !== turn.current) return;
    // The reply, coming back. Echo cancellation thins what the speakers put
    // into the microphone and does not remove it, and a slice that caught
    // the tail of an answer transcribes as somebody saying that answer.
    // Answering it starts a conversation the profile is having with itself,
    // which is what a field report on Windows watched happen.
    if (words && isEcho(words, lastSaid.current)) {
      if (wants.current) void record(w);
      return;
    }
    if (words) { setHeard(words); await turnTaken(w, words); return; }
    // Nothing said, and nothing to answer: open the ear again. When there
    // *was* something, `turnTaken` reopens it after the reply has finished
    // rather than under it.
    if (wants.current) void record(w);
  }

  function listen(w: Walking) {
    const W = window as unknown as { SpeechRecognition?: new () => any;
                                     webkitSpeechRecognition?: new () => any };
    const R = W.SpeechRecognition || W.webkitSpeechRecognition;
    if (!R || putAway() || rec.current) return;
    const mine = ++turn.current;
    const live = () => mine === turn.current;
    const r = new R();
    r.lang = w.lang;
    r.continuous = true;
    r.interimResults = true;
    let settled = "";
    let seen = 0;
    r.onresult = (e: any) => {
      if (!live()) return;
      let now = "";
      for (let i = seen; i < e.results.length; i++) {
        const row = e.results[i];
        if (row.isFinal) {
          const s = String(row[0].transcript).trim();
          if (s) settled += (settled ? " " : "") + s;
          seen = i + 1;
        } else { now += row[0].transcript; }
      }
      setHeard((settled + (now ? " " + now : "")).trim());
    };
    r.onend = () => {
      if (!live()) return;
      rec.current = null;
      const words = settled.trim();
      settled = ""; seen = 0;
      if (words) turnTaken(w, words);
      if (wants.current && !putAway()) { listen(w); return; }
      wants.current = false;
      setListening(false);
    };
    r.onerror = (e: any) => {
      if (!live()) return;
      const why = String(e?.error || "");
      if ((why === "no-speech" || why === "aborted")
          && wants.current && !putAway()) return;
      wants.current = false;
      rec.current = null;
      setListening(false);
    };
    rec.current = { stop: () => r.stop() };
    wants.current = true;
    setListening(true);
    try { r.start(); } catch { close(); }
  }

  async function turnTaken(w: Walking, message: string) {
    const mine = turn.current;
    try {
      const answer = await w.take(message);
      if (mine !== turn.current) return;
      const text = answer.text;
      setSaid(text);
      setOffline(Boolean(answer.offline));
      setHeard("");
      if (text) {
        lastSaid.current = text;
        saying.current = true;
        try {
          // The screen's own voice when it handed one over — the profile's
          // bound voice, the one somebody chose and is paying for. The
          // browser's built-in speech is the fallback and sounds like one.
          if (w.say) await w.say(text);
          else await plainVoice(text, w.lang);
        } finally {
          saying.current = false;
        }
      }
    } catch {
      if (mine === turn.current) setSaid(tr("walk.lost", w.lang as never));
    } finally {
      // The ear opens again after the answer has finished, not during it.
      // Interrupting is a real thing to want and this is not the shape that
      // gives it: the recorder posts fixed slices rather than listening
      // continuously, so an ear open under the reply hears the reply.
      if (mine === turn.current && wants.current) {
        if (w.hears) void record(w); else listen(w);
      }
    }
  }


  if (!who) return null;
  return (
    <div className="walk-strip" role="status" aria-live="polite">
      <button className="walk-end" onClick={() => { close(); stopWalking(); }}>
        {tr("walk.end", who.lang as never)}
      </button>
      <span className="walk-who">{who.shownName}</span>
      <span className="muted small walk-state">
        {asleep ? (who.hears ? tr("walk.aloft", who.lang as never)
                             : tr("walk.asleep", who.lang as never))
                : listening ? tr("walk.listening", who.lang as never)
                            : tr("walk.quiet", who.lang as never)}
      </span>
      {/* Who answered, when it was not the model. It qualifies the words,
          so it sits with them rather than with the ear's own state. */}
      {offline && (
        <span className="muted small walk-offline">
          {tr("walk.offline", who.lang as never)}
        </span>
      )}
      {trouble && <span className="walk-trouble">{trouble}</span>}
      {/* The way back. A strip that says it stopped and offers nothing is
          a dead end somebody has to leave the app to escape — and on the
          platform this exists for, they have just come back into it. */}
      {trouble && (
        <button className="walk-again"
                onClick={() => {
                  setTrouble("");
                  const w = walking();
                  if (w) { if (w.hears) void record(w); else listen(w); }
                }}>
          {tr("walk.again", who.lang as never)}
        </button>
      )}
      {(heard || said) && !trouble && (
        <span className="walk-words">{heard || said}</span>
      )}
    </div>
  );
}
