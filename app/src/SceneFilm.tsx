import { useEffect, useRef, useState } from "react";
import { api, getBase, type SceneRender } from "./api";
import { fill, t as tr, type Lang } from "./l10n";

/**
 * The reply, as footage — and the wait in between.
 *
 * A turn on the video road comes back with a row, not a video: rendering
 * is minutes and a reply is not, so `auto_render` starts the job, records
 * it, and returns. This is the other end of that. It polls the row until
 * it settles and then plays what came back.
 *
 *     asked     show the video
 *     mattered  say what is happening while there isn't one
 *
 * Four states, and three of them have no video in them. A component that
 * only draws the finished case leaves the common case — a person who just
 * read a reply and is looking at nothing — with a blank space and no way
 * to tell a render in progress from one that failed, or from a ceiling
 * they set themselves. So each says which it is, in words.
 *
 * The polling stops on unmount. That is not tidiness: leaving the screen
 * has to end the request loop, or every chat visited in a session goes on
 * asking the server about videos nobody is waiting for.
 */

/** The render clock, asked once per session rather than per bubble.
 *
 *  `give_up_after` is the server's own ceiling on a job. Duplicating the
 *  number here would let a deployment that raised it keep a screen that
 *  quits early, so it is fetched — but a fetch per message bubble to
 *  learn one constant is a request storm, hence the memo. */
let doorsOnce: Promise<{ give_up_after: number }> | null = null;
function renderClock() {
  if (!doorsOnce) {
    doorsOnce = api.videoDoors()
      // A deployment that will not answer its own door still gets a
      // ceiling: a poller with no stop is worse than one that stops early.
      .catch(() => ({ give_up_after: 15 * 60 }));
  }
  return doorsOnce;
}

const POLL_EVERY = 4000;

export function SceneFilm({ scene, lang }: { scene: SceneRender; lang: Lang }) {
  const [row, setRow] = useState<SceneRender>(scene);
  const [gaveUp, setGaveUp] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);

  useEffect(() => setRow(scene), [scene]);

  useEffect(() => {
    alive.current = true;
    // "capped" carries no id — it is the ceiling answering, not a job.
    if (row.status !== "pending" || !row.id) return;
    const started = Date.now();
    const id = row.id;

    async function tick() {
      let ceiling = 15 * 60;
      try {
        ceiling = (await renderClock()).give_up_after;
      } catch {
        // Keep the fallback.
      }
      if (!alive.current) return;
      if ((Date.now() - started) / 1000 > ceiling) {
        // Not "failed". The job may well still be running, and the row
        // keeps it — saying it failed would throw away a video somebody
        // has already been billed for.
        setGaveUp(true);
        return;
      }
      try {
        const got = await api.videoFollow(id);
        if (!alive.current) return;
        setRow(got);
        if (got.status === "pending") {
          timer.current = setTimeout(() => void tick(), POLL_EVERY);
        }
      } catch {
        // An unreachable poll is not a failed render either. Try again.
        if (alive.current) {
          timer.current = setTimeout(() => void tick(), POLL_EVERY);
        }
      }
    }
    timer.current = setTimeout(() => void tick(), POLL_EVERY);

    return () => {
      alive.current = false;
      if (timer.current) clearTimeout(timer.current);
      timer.current = null;
    };
  }, [row.status, row.id]);

  if (row.status === "capped") {
    return (
      <div className="bubble-scene capped" data-screen="209">
        {fill(tr("chat.scene.capped", lang), {
          left: String(row.left ?? 0),
          cap: String(row.daily_seconds ?? 0),
        })}
      </div>
    );
  }

  if (row.status === "failed") {
    return (
      <div className="bubble-scene failed" data-screen="209">
        <span>{tr("chat.scene.failed", lang)}</span>
        {row.detail && <em className="muted small"> {row.detail}</em>}
      </div>
    );
  }

  if (row.status === "done" && row.video_url) {
    const src = row.video_url.startsWith("http")
      ? row.video_url : getBase() + row.video_url;
    return (
      <div className="bubble-scene done" data-screen="209">
        {/* Marked on the surface as well as in storage. `asset_is_marked`
            decides by path and the file itself carries the badge, but a
            person watching a video in a chat bubble reads the caption
            under it, not the URL it came from. */}
        <video src={src} controls playsInline preload="metadata" />
        <span className="bubble-scene-ai">{tr("chat.scene.ai", lang)}</span>
      </div>
    );
  }

  if (gaveUp) {
    return (
      <div className="bubble-scene waiting" data-screen="209">
        {tr("chat.scene.gaveup", lang)}
      </div>
    );
  }

  return (
    <div className="bubble-scene making" aria-live="polite"
         data-screen="209">
      {fill(tr("chat.scene.making", lang),
            { seconds: String(row.seconds ?? 0) })}
    </div>
  );
}
