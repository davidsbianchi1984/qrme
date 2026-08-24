import { useEffect, useRef, useState } from "react";
import { putAway, whenPutAway } from "./away";
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
  const rec = useRef<{ stop: () => void } | null>(null);
  const wants = useRef(false);
  const turn = useRef(0);

  useEffect(() => onWalk(setWho), []);

  // The page going away closes the ear and says so. Coming back does not
  // reopen it: a microphone that restarts itself because a tab regained
  // focus is one nobody pressed for, which is the line this whole component
  // is on the right side of.
  useEffect(() => whenPutAway(
    () => { setAsleep(true); close(); },
    () => setAsleep(false)), []);

  useEffect(() => {
    if (!who) { close(); return; }
    listen(who);
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
    try {
      const answer = await w.take(message);
      const text = answer.text;
      setSaid(text);
      setOffline(Boolean(answer.offline));
      setHeard("");
      if (text && "speechSynthesis" in window) {
        const u = new SpeechSynthesisUtterance(text);
        u.lang = w.lang;
        window.speechSynthesis.speak(u);
      }
    } catch {
      setSaid(tr("walk.lost", w.lang as never));
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
        {asleep ? tr("walk.asleep", who.lang as never)
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
      {(heard || said) && (
        <span className="walk-words">{heard || said}</span>
      )}
    </div>
  );
}
