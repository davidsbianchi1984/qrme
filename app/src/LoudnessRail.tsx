import { useRef, useState } from "react";
import { setSpokenLoudness, spokenLoudness } from "./spoken";
import { t as tr, visitorLang } from "./l10n";

/**
 * The dial-down for spoken audio, on every screen that can make a sound —
 * which, since the shell owns it now, is every screen.
 *
 * It began on the Voice screen, which is where a person *configures* a
 * voice — but the places a person *hears* one are the talk face, the agent
 * and a room, none of which could reach it: too loud mid-conversation
 * meant leaving the conversation to fix it. The shell owns the rail for
 * the same reason it owns Help and the task lights — every screen has it
 * without each screen having to remember.
 *
 *     asked     can I dial it down where I hear it
 *     mattered  a volume control on the one screen that plays no
 *               conversation is a thermostat in the garage
 *
 * Same posture as before: full blast is the default, the rail only
 * attenuates, remembered per device, applied to the sentence already in
 * the ear (see spoken.ts). Fixed to the right edge, moving nothing —
 * a control that moves other controls to exist costs more than it gives.
 */
export function LoudnessRail() {
  const lang = visitorLang();
  const [loud, setLoud] = useState(() => spokenLoudness());
  // Asleep by default -- "let's hide the volume button... reappear but
  // fade away after a short while." A control pinned over every screen
  // earns its keep by being invisible until wanted: asleep, it is a
  // faint sliver tucked into the edge; touched, it wakes whole; left
  // alone three seconds, it fades back. The phone's own volume keys
  // never reach a web page (no browser exposes them), so the wakes are
  // the ones a page can actually see: a touch on the sliver, a drag on
  // the slider. Position, layer and look moved to styles.css so the
  // sleep transform can win -- an inline transform outranks any class.
  const [awake, setAwake] = useState(false);
  const dozer = useRef<number | null>(null);
  function wake() {
    setAwake(true);
    if (dozer.current) window.clearTimeout(dozer.current);
    dozer.current = window.setTimeout(() => setAwake(false), 3000);
  }
  return (
    <div className={"loudness-rail" + (awake ? " awake" : " asleep")}
         title={tr("voice.spoken.loud", lang)}
         onPointerEnter={wake} onPointerDown={wake}
         onTouchStart={wake}>
      <span className="muted small loudness-count" aria-hidden="true">
        {Math.round(loud * 100)}%
      </span>
      <input type="range" min={5} max={100} step={5}
             value={Math.round(loud * 100)}
             aria-label={tr("voice.spoken.loud", lang)}
             style={{ writingMode: "vertical-lr", direction: "rtl",
                      height: 110, width: 22 }}
             onChange={(e) => {
               const v = Number(e.target.value) / 100;
               setLoud(v);
               setSpokenLoudness(v);
               wake();
             }} />
    </div>
  );
}
