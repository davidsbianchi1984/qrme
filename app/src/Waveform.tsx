/** Bars that mean something.
 *
 * The design this came from had a waveform under the figure that animated
 * permanently, which makes it decoration — and worse than decoration, because
 * bars moving while nothing is being heard say the microphone is live when it
 * is not. A person deciding whether it is safe to speak reads that strip.
 *
 *     asked     does the screen have a waveform
 *     mattered  does it move only when something is moving
 *
 * `presence.waveformOf` decides; this only draws. Four readings and each one
 * is a different claim:
 *
 *     in     their voice, coming in     — the microphone is open
 *     out    the profile's, going out   — audio is playing
 *     busy   neither, and working       — a turn is out, or a file is read
 *     still  nothing is happening       — flat, and it means flat
 *
 * `busy` deliberately does not look like either voice. A spinner shape rather
 * than a speech shape, because the one thing it must not say is that somebody
 * is talking.
 */

import { useEffect, useRef } from "react";
import type { Presence } from "./presence";
import { waveformOf } from "./presence";
import { t as tr } from "./l10n";

const BARS = 21;

export function Waveform({ presence, lang }: {
  presence: Presence; lang: string;
}) {
  const reading = waveformOf(presence);
  const ref = useRef<HTMLDivElement | null>(null);
  const frame = useRef<number | null>(null);

  useEffect(() => {
    const host = ref.current;
    if (!host) return;
    const bars = Array.from(
      host.querySelectorAll<HTMLElement>(".wf-bar"));

    if (reading === "still") {
      // Flat, and left flat — no residual animation frame keeping a dead
      // strip alive. This is the state the surface is in most of the time.
      bars.forEach((b) => { b.style.transform = "scaleY(0.08)"; });
      return;
    }

    // Deterministic rather than random: a strip that jitters differently on
    // every render reads as noise, and the point is that it reads as a
    // reading. Phase per bar, amplitude per state.
    const start = performance.now();
    const speed = reading === "busy" ? 0.0016 : 0.0042;
    const spread = reading === "busy" ? 0.55 : 1;
    const tick = (now: number) => {
      const e = (now - start) * speed;
      bars.forEach((b, i) => {
        const centred = 1 - Math.abs(i - (BARS - 1) / 2) / ((BARS - 1) / 2);
        const wave = Math.sin(e + i * 0.55) * 0.5 + 0.5;
        // `out` swells from the middle — a voice leaving the figure. `in`
        // is flatter across, the way a room's level is.
        const shape = reading === "out" ? 0.25 + centred * 0.75 : 0.7;
        const h = 0.08 + wave * shape * spread * 0.92;
        b.style.transform = `scaleY(${h.toFixed(3)})`;
      });
      frame.current = requestAnimationFrame(tick);
    };
    frame.current = requestAnimationFrame(tick);
    return () => {
      if (frame.current !== null) cancelAnimationFrame(frame.current);
      frame.current = null;
    };
  }, [reading]);

  return (
    <div ref={ref}
         data-screen="199"
         className={`waveform wf-${reading}`}
         // The strip is a reading, so it is announced as one rather than
         // left as decoration a screen reader walks into and cannot name.
         role="img"
         aria-label={tr(`wave.${reading}`, lang)}>
      {Array.from({ length: BARS }, (_, i) => (
        <span key={i} className="wf-bar" />
      ))}
    </div>
  );
}
