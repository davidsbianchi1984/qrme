import { useState } from "react";
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
  return (
    <div className="loudness-rail" title={tr("voice.spoken.loud", lang)}
         style={{ position: "fixed", right: 6, top: "50%",
                  transform: "translateY(-50%)",
                  // Above the talk overlay (60) and the room stage (80):
                  // those are the screens the sound comes out of, and a
                  // rail underneath them is the old problem in a new
                  // place. Below the footsteps (90) and the version
                  // guard (100), which outrank everything by design.
                  zIndex: 85,
                  display: "flex", flexDirection: "column",
                  alignItems: "center", gap: 4, padding: "8px 2px",
                  borderRadius: 12, background: "rgba(20,18,40,0.55)" }}>
      <span className="muted small" aria-hidden="true">
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
             }} />
    </div>
  );
}
