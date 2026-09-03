import { useEffect, useRef, useState } from "react";
import { api, getBase, type SceneRender } from "./api";

/**
 * Following a render until it settles, in one place.
 *
 * Two surfaces watch the same row — the bubble under a reply in a
 * conversation, and the frame a room puts the turn in — and they had no
 * business each carrying their own poller. Two copies of a loop with a
 * lifecycle, a give-up clock and a stop-on-unmount is two chances to get
 * one of the three wrong, and the one that goes wrong quietly is the
 * stop: a screen left polling has no symptom on the screen itself.
 *
 *     asked     is the render finished
 *     mattered  does asking end when the thing that asked goes away
 */

/** The render clock, asked once per session rather than once per watcher.
 *
 *  `give_up_after` is the server's own ceiling on a job. Duplicating the
 *  number here would let a deployment that raised it keep screens that
 *  quit early, so it is fetched — but a fetch per watcher to learn one
 *  constant is a request storm, hence the memo. */
let doorsOnce: Promise<{ give_up_after: number }> | null = null;

export function renderClock() {
  if (!doorsOnce) {
    doorsOnce = api.videoDoors()
      // A deployment that will not answer its own door still gets a
      // ceiling: a poller with no stop is worse than one that stops early.
      .catch(() => ({ give_up_after: 15 * 60 }));
  }
  return doorsOnce;
}

export const POLL_EVERY = 4000;

/** Watch one render. Returns the row as it stands and whether the wait
 *  was given up on — which is not the same as failed, and must never be
 *  drawn as if it were. */
export function useRenderRow(scene: SceneRender) {
  const [row, setRow] = useState<SceneRender>(scene);
  const [gaveUp, setGaveUp] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);

  useEffect(() => { setRow(scene); setGaveUp(false); }, [scene]);

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

  return { row, gaveUp };
}

/** The address a video actually plays from. A render comes back as an
 *  absolute URL from the service or a path on this deployment, and a
 *  `<video>` cannot tell which without being told. */
export function playable(url: string) {
  return url.startsWith("http") ? url : getBase() + url;
}


/** The media id behind a served `/media/<id>.<ext>` url — the handle the
 *  burned download is asked for by. Null for anything not served here. */
export function mediaIdOf(url: string): string | null {
  const m = /\/media\/(med_[A-Za-z0-9]+)\.[a-z0-9]+$/i.exec(url);
  return m ? m[1] : null;
}
